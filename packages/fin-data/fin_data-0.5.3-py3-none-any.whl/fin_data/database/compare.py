from typing import List, Optional, Set, Tuple, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .engine import cached_engine_from_env
from .utils import as_table, logger


def is_same_col_type(col1: sa.Column, col2: sa.Column) -> bool:
    """Check if two columns have the same datatype.

    Args:
        col1 (sa.Column): Column that should be compared with `col2`
        col2 (sa.Column): Column that should be compared with `col1`

    Returns:
        bool: True if columns have the same datatype.
    """
    # if columns are enum type, check that they have the same name options.
    if hasattr(col1.type, "enums") and hasattr(col2.type, "enums"):
        return set(col1.type.enums) == set(col2.type.enums)

    # check for postgresql/SQLAlchemy equivalent types.
    if col1.type.compile(dialect=postgresql.dialect()) == col2.type.compile(
        dialect=postgresql.dialect()
    ):
        return True
    # SQLAlchemy only has float, postgres has both float and double.
    eq = (sa.Float, postgresql.DOUBLE_PRECISION)
    if type(col1.type) in eq and type(col2.type) in eq:
        return True
    return False


def column_type_mismatch(
    sa_obj: Union[sa.Table, DeclarativeMeta], reflected_table: sa.Table
) -> List[str]:
    """Check that column types in an SQLAlchemy table or entity match the corresponding database table.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy table or entity.
        reflected_table (sa.Table): Reflected database table corresponding to `sa_obj`.

    Returns:
        List[str]: Names of columns that have mismatched datatypes.
    """
    # check that data types match.
    sa_table = as_table(sa_obj)
    mismatch = []
    for col in set(reflected_table.columns.keys()).intersection(
        sa_table.columns.keys()
    ):
        if not is_same_col_type(
            sa_col := sa_table.columns[col], db_col := reflected_table.columns[col]
        ):
            mismatch.append(col)
            logger.error(
                f"Object column type {sa_col} does not match database column type {db_col}."
            )
    return mismatch


def column_name_mismatch(
    sa_obj: Union[sa.Table, DeclarativeMeta], reflected_table: sa.Table
) -> Tuple[Set[str], Set[str]]:
    """Check that column names in an SQLAlchemy table or entity match the corresponding database table.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy table or entity.
        reflected_table (sa.Table): Reflected database table corresponding to `sa_obj`.

    Returns:
        Tuple[Set[str], Set[str]]: Names of columns that have mismatched names.
    """
    sa_table = as_table(sa_obj)
    entity_columns = [c.name for c in sa_table.columns.values()]
    db_columns = [c.name for c in reflected_table.columns.values()]
    entity_cols_not_in_db = set(entity_columns).difference(db_columns)
    if entity_cols_not_in_db:
        logger.error(
            f"Entity column(s) ({entity_cols_not_in_db}) are not in database table {reflected_table.name}"
        )
    db_cols_not_in_sa = set(db_columns).difference(entity_columns)
    if db_cols_not_in_sa:
        logger.warning(
            f"Database columns ({db_cols_not_in_sa}) are not in entity {reflected_table.name}"
        )
    return db_cols_not_in_sa, entity_cols_not_in_db


def primary_key_mismatch(
    sa_obj: Union[sa.Table, DeclarativeMeta], reflected_table: sa.Table
) -> Tuple[Set[str], Set[str]]:
    """Check that primary key in an SQLAlchemy table or entity matches the corresponding database table.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy table or entity.
        reflected_table (sa.Table): Reflected database table corresponding to `sa_obj`.

    Returns:
        Tuple[Set[str], Set[str]]: Names of columns that have mismatched primary key.
    """
    # Check if primary keys in entty match primary keys in database.
    sa_table = as_table(sa_obj)
    sa_pkeys = {c.name for c in sa_table.primary_key.columns}
    db_pkeys = {c.name for c in reflected_table.primary_key.columns}
    # check for primary keys in db but not in entity.
    if db_pk_not_in_sa := db_pkeys.difference(sa_pkeys):
        logger.error(f"Database primary key ({db_pk_not_in_sa}) not in object {sa_obj}")
    # check for primary keys in entity but not in database.
    # entities are required to have a primary key even when the database doesn't (https://docs.SQLAlchemy.org/en/14/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key)
    if sa_pk_not_in_db := sa_pkeys.difference(db_pkeys):
        logger.warning(
            f"Entity primary key ({sa_pk_not_in_db}) not in database table {reflected_table.name}"
        )
    return db_pk_not_in_sa, sa_pk_not_in_db


def foreign_key_mismatch(
    sa_obj: Union[sa.Table, DeclarativeMeta], reflected_table: sa.Table
) -> Tuple[Set[str], Set[str]]:
    """Check that foreign key in an SQLAlchemy table or entity matches the corresponding database table.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy table or entity.
        reflected_table (sa.Table): Reflected database table corresponding to `sa_obj`.

    Returns:
        Tuple[Set[str], Set[str]]: Names of columns that have mismatched foreign key.
    """
    # check for foreign key mismatches.
    sa_table = as_table(sa_obj)
    sa_fkeys = {
        fk.target_fullname
        for col in sa_table.columns.values()
        for fk in col.foreign_keys
    }
    db_fkeys = {
        fk.target_fullname
        for col in reflected_table.columns.values()
        for fk in col.foreign_keys
    }
    # check for foreign keys in db but not in entity.
    if db_fk_not_in_sa := db_fkeys.difference(sa_fkeys):
        logger.error(f"Database foreign key ({db_fk_not_in_sa}) not in object {sa_obj}")
    # check for foreign keys in entity but not in database.
    if sa_fk_not_in_db := sa_fkeys.difference(db_fkeys):
        logger.warning(
            f"Entity foreign key ({sa_fk_not_in_db}) not in database table {reflected_table.name}"
        )
    return db_fk_not_in_sa, sa_fk_not_in_db


def nullable_column_mismatch(
    sa_obj: Union[sa.Table, DeclarativeMeta], reflected_table: sa.Table
) -> Tuple[Set[str], Set[str]]:
    """Check that nullable columns in an SQLAlchemy table or entity match the corresponding database table.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy table or entity.
        reflected_table (sa.Table): Reflected database table corresponding to `sa_obj`.

    Returns:
        Tuple[Set[str], Set[str]]: Names of columns that have mismatched nullable columns.
    """
    # check for nullable column mismatches.
    sa_table = as_table(sa_obj)
    entity_nullable_cols = {
        col_name for col_name, col in sa_table.columns.items() if col.nullable
    }
    db_nullable_cols = {
        col_nams for col_nams, col in reflected_table.columns.items() if col.nullable
    }
    # check for nullable columns in entity that are not in database.
    entity_nullable_not_in_db = entity_nullable_cols.difference(db_nullable_cols)
    if entity_nullable_not_in_db:
        logger.error(
            f"Object {sa_obj} nullable column(s) ({entity_nullable_not_in_db}) are not in database table {reflected_table.name}"
        )
    db_nullable_not_in_sa = db_nullable_cols.difference(entity_nullable_cols)
    # entities are required to have a primary key even when the database doesn't,
    # if this is the case, then database column will not be nullabe in entity.
    if db_nullable_not_in_sa:
        logger.warning(
            f"Database nullable columns ({db_nullable_not_in_sa}) are not nullable in entity {reflected_table.name}"
        )
    return db_nullable_not_in_sa, entity_nullable_not_in_db


def matches_db(
    to_check: Union[sa.Table, DeclarativeMeta], engine: Optional[Engine] = None
) -> bool:
    """Check that an SQLAlchemy table or entity has columns and constaints matching it's corresponding database table.

    Args:
        to_check (Union[sa.Table, DeclarativeMeta]): An SQLAlchemy entity or table.
        engine (Optional[Engine]): Engine connected to the database being checked.

    Returns:
        bool: True if database table matches SQLAlchemy model, else False.
    """
    logger.info(f"Checking that {to_check} columns match the database table.")
    table = as_table(to_check)

    engine = engine or cached_engine_from_env()

    if not engine.dialect.has_table(
        table_name=table.name, schema=table.schema or "public"
    ):
        logger.warning(f"Database has no table named {table.name}!")
        return False

    # reflect database columns table to object.
    reflected_table = sa.Table(
        table.name,
        sa.MetaData(schema=table.schema),
        autoload_with=engine,
    )

    return not any(
        len(error)
        for error in (
            column_type_mismatch(to_check, reflected_table),
            *primary_key_mismatch(to_check, reflected_table),
            *foreign_key_mismatch(to_check, reflected_table),
            *nullable_column_mismatch(to_check, reflected_table),
            *column_name_mismatch(to_check, reflected_table),
        )
    )
