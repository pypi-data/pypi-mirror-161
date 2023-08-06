from collections import defaultdict, deque
from typing import Any, Callable, Dict, List, Optional, Union

import sqlalchemy as sa
from cytoolz.itertoolz import partition_all
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.exc import CompileError, IntegrityError
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .create import async_create_table
from .engine import cached_async_engine_from_env
from .utils import as_table, create_column_name_filter, get_logger, groupby_columns


class DBLoader:
    @classmethod
    async def create(
        cls,
        sa_obj: Union[sa.Table, DeclarativeMeta],
        on_duplicate_key_update: Optional[Union[bool, List[str]]] = True,
        row_batch_size: int = 1500,
        remove_duplicate_keys: bool = True,
        drop_rows_missing_key: bool = True,
        batch_by_names_present: bool = True,
        drop_names: Optional[List[str]] = None,
        name_to_name: Optional[Dict[str, str]] = None,
        name_converter: Callable[[str], str] = None,
        name_to_name_converter: Optional[Dict[str, Callable[[str], str]]] = None,
        value_to_value: Optional[Dict[Any, Any]] = None,
        name_to_value: Optional[Dict[str, Any]] = None,
        value_converter: Optional[Callable[[Any], Any]] = None,
        name_to_value_converter: Optional[Dict[str, Callable[[Any], Any]]] = None,
        drop_values: Optional[List[str]] = None,
        name_to_drop_values: Optional[Dict[str, List[str]]] = None,
        drop_on_type_conversion_fail: bool = True,
        async_engine: Optional[AsyncEngine] = None,
    ):
        """Load data rows to a postgresql database.
        Name converters are the first thing applied,
        so arguments mapping from name should use the name in converted form.

        Args:
            sa_obj (Union[sa.Table, DeclarativeMeta]): The SQLAlchemy table or entity corresponding to the database table that rows will be loaded to.
            remove_duplicate_keys (bool, optional): Remove duplicates from upsert batches. Defaults to True.
            batch_by_names_present (bool, optional): Group rows by columns present and execute upsert statement for each group. Defaults to True.
            on_duplicate_key_update (Union[bool, List[str]], optional): List of columns that should be updated when primary key exists, or True for all columns, False for no columns, None if duplicates should not be checked (i.e. a normal INSERT). Defaults to True.
            async_engine (Optional[AsyncEngine], optional): The engine to use to execute sql statements. Defaults to None.
            row_batch_size (int): The maximum number of rows to upsert at once.
            name_to_name (Optional[Dict[str, str]], optional): Map column name to desired column name. Defaults to None.
            name_converter (Callable, optional): A formatting function to apply to every name. Defaults to None.
            name_to_name_converter (Optional[Dict[str, Callable]], optional): Map column name to formatting function. Defaults to None.
            drop_names (Optional[List[str]], optional): Names of columns that should be filtered from rows. Defaults to None.
            value_to_value (Optional[Dict[Any, Any]], optional): Map value to desired value. Defaults to None.
            name_to_value: (Optional[Dict[str, Any]], optional): Map column name to desired column value. Defaults to None.
            value_converter (Optional[Callable], optional): A conversion function to apply to every value. Defaults to None.
            name_to_value_converter (Optional[Dict[str, Callable]], optional): Map column name to column value conversion function. Defaults to None.
            drop_values (Optional[List[str]], optional): Values where columns should be dropped if they are that value. (e.g ['null', None, 'Na']). Defaults to None.
            drop_on_type_conversion_fail (bool, optional): Remove column from row if conversion fails. Defaults to False.
            kwargs: keyword arguments for initializing ColumnNameFilter and ColumnValueFilter.
        """
        self = cls()
        self.row_batch_size = row_batch_size
        # If doing non-deterministic column dropping, we need to group by columns present.
        self.batch_by_names_present = batch_by_names_present or any(
            (drop_values, name_to_drop_values, drop_on_type_conversion_fail)
        )
        self.on_duplicate_key_update = on_duplicate_key_update

        self.table = as_table(sa_obj)
        self.logger = get_logger(f"fin-data-db[{self.table.name}]")
        self._primary_key_column_names = {
            c.name for c in self.table.primary_key.columns
        }
        if not self._primary_key_column_names:
            # not applicable because there are no keys.
            drop_rows_missing_key = False
            self.on_duplicate_key_update = None
            self.remove_duplicate_keys = False
        else:
            self.remove_duplicate_keys = remove_duplicate_keys

        # determine what should be updated when there is an existing primary key.
        if self.on_duplicate_key_update == True:
            # update all columns that aren't primary key.
            self.on_duplicate_key_update = [
                col_name
                for col_name, col in self.table.columns.items()
                if not col.primary_key
            ]
        if self.on_duplicate_key_update:
            self._build_statement = self._build_upsert_update_statement
        elif self.on_duplicate_key_update == False:
            self._build_statement = self._build_upsert_ignore_statement
        elif self.on_duplicate_key_update is None:
            self._build_statement = self._build_insert_statement
        else:
            raise ValueError(
                f"Invalid argument for on_duplicate_key_update: {self.on_duplicate_key_update}"
            )

        self.filters = {}
        # do column name filtering first, so other functions will use the filtered names.
        if column_name_filter := create_column_name_filter(
            name_to_name, name_converter, name_to_name_converter
        ):
            self.filters["column_name_filter"] = column_name_filter

        drop_names = drop_names or []
        columns_names_to_load = {
            str(c) for c in self.table.columns.keys() if c not in drop_names
        }
        self.filters["columns_names_to_load"] = lambda rows: [
            {c: row[c] for c in columns_names_to_load if c in row} for row in rows
        ]
        if drop_rows_missing_key:
            self.filters["drop_rows_missing_key"] = lambda rows: [
                row
                for row in rows
                if all(c in row for c in self._primary_key_column_names)
            ]

        if self.remove_duplicate_keys:
            self.filters["remove_duplicate_keys"] = self._remove_duplicate_keys

        if value_to_value:
            self.filters["value_to_value"] = lambda rows: [
                {k: value_to_value.get(v, v) for k, v in row.items()} for row in rows
            ]
        if drop_values:
            if not isinstance(drop_values, (list, tuple, set)):
                drop_values = [drop_values]
            self.filters["drop_values"] = lambda rows: [
                {k: v for k, v in row.items() if v not in drop_values} for row in rows
            ]
        if name_to_drop_values:
            self.filters["name_to_drop_values"] = lambda rows: [
                {k: v for k, v in row.items() if name_to_drop_values.get(k) != v}
                for row in rows
            ]
        if name_to_value:
            self.filters["name_to_value"] = lambda rows: [
                {k: name_to_value.get(k, v) for k, v in row.items()} for row in rows
            ]

        col_val_cvts = defaultdict(list)
        if value_converter:
            for c in columns_names_to_load:
                col_val_cvts[c].append(value_converter)
        if name_to_value_converter:
            for k, v in name_to_value_converter.items():
                col_val_cvts[k].append(v)
        if col_val_cvts:

            def convert_column_values(rows):
                converted_rows = []
                for row in rows:
                    to_remove = set()
                    for col, val_cvts in col_val_cvts.items():
                        if col in row:
                            for vc in val_cvts:
                                try:
                                    row[col] = vc(row[col])
                                except Exception as e:
                                    msg = f"Error converting column '{col}' value {row[col]}: {e}"
                                    if drop_on_type_conversion_fail:
                                        self.logger.error(msg)
                                        to_remove.add(col)
                                    else:
                                        raise type(e)(msg)
                    for col in to_remove:
                        del row[col]
                    converted_rows.append(row)
                return converted_rows

            self.filters["convert_column_values"] = convert_column_values

        self.logger.info(
            f"{len(self.filters)} filters will be applied before loading rows: {list(self.filters.keys())}"
        )

        self.engine = async_engine or cached_async_engine_from_env()
        self.row_buffer = []
        # create table if it doesn't already exist.
        async with self.engine.begin() as conn:
            await async_create_table(conn, self.table)
        return self

    async def add(self, row: Dict[str, Any]):
        self.row_buffer.append(row)
        if len(self.row_buffer) >= self.row_batch_size:
            await self.load()

    async def extend(self, rows: List[Dict[str, Any]]):
        self.row_buffer.extend(rows)
        if len(self.row_buffer) >= self.row_batch_size:
            await self.load()

    async def load(
        self, rows: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[Dict[str, Any]]]:
        """Load rows to the database.

        Args:
            rows (List[Dict[str, Any]]): The rows to load.

        Returns:
            List[List[Dict[str, Any]]]: The groups of rows that were loaded.
        """
        if rows:
            self.row_buffer.extend(rows)
        # take all rows in the buffer.
        if not (rows := self.row_buffer):
            return []
        # start a new buffer.
        self.row_buffer = []

        if not (rows := self._filter_rows(rows)):
            return []

        row_groups = groupby_columns(rows) if self.batch_by_names_present else [rows]
        batches = deque()
        # split rows into smaller batches if there are too many to insert at once.
        for rows in row_groups:
            for batch in partition_all(self.row_batch_size, rows):
                batches.append(batch)
        # upsert all batches.
        self.logger.info(
            f"Loading {len(rows)} rows ({len(batches)} batches) to the database."
        )
        loaded_batches = []
        async with self.engine.begin() as conn:
            while len(batches):
                rows = batches.popleft()
                statement = self._build_statement(rows)
                self.logger.info(f"Loading {len(rows)} rows to {self.table}")
                try:
                    await conn.execute(statement)
                    loaded_batches.append(rows)
                except IntegrityError as ie:
                    if (
                        not self.remove_duplicate_keys
                        and "duplicate key value violates unique constraint"
                        in ie._message()
                    ):
                        batches.append(self._remove_duplicate_keys(rows))
                    else:
                        raise ie

                except CompileError as ce:
                    if (
                        not self.batch_by_names_present
                        and "is explicitly rendered as a boundparameter in the VALUES clause"
                        in ce._message()
                    ):
                        for rows in groupby_columns(rows):
                            batches.append(rows)
                    else:
                        raise ce
        return loaded_batches

    def filtered_rows(
        self, rows: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        rows = rows + self.row_buffer if rows else self.row_buffer
        return self._filter_rows(rows)

    def _filter_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # filter rows.
        for filter_name, filter_func in self.filters.items():
            if not (rows := filter_func(rows)):
                self.logger.warning(
                    f"No rows remain after applying filter function: {filter_name}"
                )
                return
        return rows

    def _remove_duplicate_keys(
        self, rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove rows that repeat a primary key.
        Multiple row in the same upsert statement can not have the same primary key.

        Args:
            rows (List[Dict[str, Any]]): Data row, possibly containing duplicates.

        Returns:
            List[Dict[str, Any]]: Duplicate-free data rows.
        """
        unique_key_rows = {
            tuple([row[c] for c in self._primary_key_column_names]): row for row in rows
        }
        unique_key_rows = list(unique_key_rows.values())
        if (unique_count := len(unique_key_rows)) < (row_count := len(rows)):
            self.logger.warning(
                f"{row_count - unique_count}/{row_count} rows had a duplicate primary key and will not be loaded."
            )
        return unique_key_rows

    def _build_insert_statement(self, rows: List[Dict[str, Any]]) -> Insert:
        """Construct a statement to insert `rows`.

        Args:
            rows (List[Dict[str,Any]]): The rows that will be loaded.

        Returns:
            Insert: An insert statement.
        """
        return postgresql.insert(self.table).values(rows)

    def _build_upsert_update_statement(self, rows: List[Dict[str, Any]]) -> Insert:
        """Construct a statement to load `rows`.

        Args:
            rows (List[Dict[str,Any]]): The rows that will be loaded.

        Returns:
            Insert: An upsert statement.
        """
        statement = postgresql.insert(self.table).values(rows)
        # check column of first row (all rows should have same columns)
        if len(
            on_duplicate_key_update := [
                c for c in self.on_duplicate_key_update if c in rows[0]
            ]
        ):
            statement = statement.on_conflict_do_update(
                index_elements=self._primary_key_column_names,
                set_={k: statement.excluded[k] for k in on_duplicate_key_update},
            )
        else:
            # rows do not have anything to update..
            statement = statement.on_conflict_do_nothing(
                index_elements=self._primary_key_column_names
            )
        return statement

    def _build_upsert_ignore_statement(self, rows: List[Dict[str, Any]]) -> Insert:
        """Construct a statement to load `rows`.

        Args:
            rows (List[Dict[str,Any]]): The rows that will be loaded.

        Returns:
            Insert: An upsert statement.
        """
        return (
            postgresql.insert(self.table)
            .values(rows)
            .on_conflict_do_nothing(index_elements=self._primary_key_column_names)
        )
