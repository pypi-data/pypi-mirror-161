from datetime import datetime
from functools import cache
from typing import Any, Dict, List, Optional, Union

import sqlalchemy as sa
from ready_logger import get_logger
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .load import DBLoader
from .utils import as_table, create_row_id_generator


class SourcesDBLoader:
    @classmethod
    async def create(
        cls,
        source: str,
        row_id_column: str = "data_id",
        generate_row_id: bool = True,
        db_loader: Optional[DBLoader] = None,
        **kwargs,
    ):
        """Upsert rows to a table and also upsert source metadata to the corresponding sources table.

        Args:
            source (str): The source that the data is from.
            row_id_column (str): The column that should be used to join to the data table to the sources table.
            generate_row_id (bool): Assign a data-generated ID to `row_id_column` for each row.
            logger (Logger): The logger instance to use for logging.
            db_loader (DBLoader): The DBLoader that will be used to load rows.
            kwargs: If `db_loader` argument is not provided, DBLoader kwargs may be provided and a new `DBLoader` will be initialized.

        Raises:
            RuntimeError: If the db_loader's table does not contain column `row_id_column`.
        """
        self = cls()
        self.source = source
        self.row_id_column = row_id_column
        self.generate_row_id = generate_row_id
        self.db_loader = db_loader or await DBLoader.create(**kwargs)
        if self.row_id_column not in self.db_loader.table.columns:
            raise RuntimeError(
                f"Table {self.db_loader.table.name} must contain column `{self.row_id_column}` to be linked to a sources table."
            )
        self._row_id_generator = (
            create_row_id_generator(self.db_loader.table, self.row_id_column)
            if generate_row_id
            else None
        )
        self._sources_table = self.get_sources_table(self.db_loader, self.row_id_column)
        self.logger = get_logger(f"fin-data-db[{self._sources_table.name}]")
        # create sources table if it does not already exist.
        async with self.db_loader.engine.begin() as conn:
            await conn.run_sync(self._sources_table.create, checkfirst=True)
        return self

    async def load(self, rows: List[Dict[str, Any]] = None) -> None:
        """Load rows to the database and corresponding sources metadata to the sources table.

        Args:
            rows (List[Dict[str, Any]]): Data rows that should be loaded to the table.
        """
        if rows:
            self.db_loader.row_buffer.extend(rows)
        if self.generate_row_id:
            for row in self.db_loader.row_buffer:
                row[self.row_id_column] = self._row_id_generator(row)
        # load data rows to the and create statements to load source rows.
        row_groups = await self.db_loader.load()
        statements = [self._build_statement(rows) for rows in row_groups]
        # load sources metadata to sources table.
        async with self.db_loader.engine.begin() as conn:
            for statement in statements:
                self.logger.info(
                    f"Loading {len(rows)} rows to sources table. (source: {self.source})"
                )
                await conn.execute(statement)

    @staticmethod
    @cache
    def get_sources_table(
        sa_obj: Union[DBLoader, sa.Table, DeclarativeMeta], row_id_column: str
    ) -> sa.Table:
        """Create a table to contain all sources of unique rows in a table.

        Args:
            sa_obj (Union[DBLoader, sa.Table, DeclarativeMeta]): The entity to make the sources table for.

        Returns:
            sa.Table: The sources table.
        """
        table = sa_obj.table if isinstance(sa_obj, DBLoader) else as_table(sa_obj)
        _sources_table = sa.Table(
            f"{table.name}_sources",
            sa.MetaData(schema=table.schema),
            sa.Column(
                row_id_column,
                sa.VARCHAR,
                sa.ForeignKey(getattr(table.c, row_id_column), ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("source", sa.VARCHAR, primary_key=True),
            sa.Column(
                "created",
                sa.DateTime(timezone=False),
                default=datetime.utcnow,
                nullable=False,
            ),
            sa.Column(
                "last_seen",
                sa.DateTime(timezone=False),
                default=datetime.utcnow,
                nullable=False,
            ),
            sa.Column("times_seen", sa.Integer, default=1, nullable=False),
        )
        return _sources_table

    def _build_statement(self, rows: List[Dict[str, Any]]) -> Insert:
        """Construct an upsert statement to load source metadata for each row.

        Args:
            rows (List[Dict[str,Any]]): The rows to load source metadata for.

        Returns:
            Insert: An upsert statement.
        """
        statement = (
            postgresql.insert(self._sources_table)
            .values(
                [
                    {self.row_id_column: row[self.row_id_column], "source": self.source}
                    for row in rows
                ]
            )
            .on_conflict_do_update(
                index_elements=[self.row_id_column, "source"],
                set_={
                    "last_seen": datetime.utcnow(),
                    "times_seen": sa.text(
                        f'{self._sources_table.schema}."{self._sources_table.name}".times_seen + 1'
                    ),
                },
            )
        )
        return statement
