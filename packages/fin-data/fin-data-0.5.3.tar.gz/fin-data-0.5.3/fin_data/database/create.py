from typing import Union

import sqlalchemy as sa
from dynamic_imports import class_instances_from_package
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .types import HypertablePartition
from .utils import as_table, get_typed_columns, logger


async def async_create_table(
    conn: AsyncConnection,
    create_from: Union[sa.Table, DeclarativeMeta],
    recreate: bool = False,
):
    await conn.run_sync(create_table, create_from=create_from, recreate=recreate)


def create_table(
    conn: Connection,
    create_from: Union[sa.Table, DeclarativeMeta],
    recreate: bool = False,
) -> bool:
    """Create a table in the database.

    Args:
        conn (Connection): Connection to use for executing SQL statements.
        create_from (Union[sa.Table, DeclarativeMeta]): The entity or table object to create a database table for.
        recreate (bool): If table exists, drop it and recreate. Defaults to False.

    Returns:
        bool: True if a table was created, else False.
    """
    table = as_table(create_from)
    schema = table.schema or "public"
    # create schema if needed.
    if not conn.dialect.has_schema(conn, schema=schema):
        logger.info(f"Creating schema '{schema}'")
        conn.execute(sa.schema.CreateSchema(schema))
    schema_table = f"{schema}.{table.name}"
    # check if table exists.
    if conn.dialect.has_table(conn, table_name=table.name, schema=schema):
        if not recreate:
            return False
        logger.info(f"Dropping table {schema_table}")
        table.drop(conn)
    # make sure any new Enum types are created.
    create_enum_types(conn, table)
    logger.info(f"Creating table {schema_table}")
    table.create(conn)
    # create hypertable partition if needed.
    create_hypertable_partition(conn, create_from)
    return True


def create_package_tables(conn: Connection, package: str):
    tables = set(class_instances_from_package(sa.Table, package))
    for t in tables:
        create_table(conn, t)


def create_enum_types(
    conn: Connection, sa_obj: Union[sa.Table, DeclarativeMeta]
) -> None:
    """Create enum types if they do not already exist in the database.
    This is necessary because sa.Table.create has no way to handle columns that have an enum type that already exists in the Database.

    Args:
        conn (Connection): Connection to use for executing SQL statements.
        sa_obj (Union[sa.Table, DeclarativeMeta]): The table who's enums should be checked.
    """
    table = as_table(sa_obj)
    # all enums present in table.
    enums = [
        col.type
        for col in table.columns.values()
        if isinstance(col.type, postgresql.ENUM)
    ]
    for enum in enums:
        # check if enum type exists, create it if it doesn't.
        enum.create(conn, checkfirst=True)
        # prevent table.create for attempting to create the enum type.
        enum.create_type = False


def create_hypertable_partition(
    conn: Connection, sa_obj: Union[sa.Table, DeclarativeMeta]
) -> None:
    """Create a hypertable partition if table or entity has a column that is flagged as a hypertable partition column.

    Args:
        conn (Connection): Connection to use for executing SQL statements.
        sa_obj (Union[sa.Table, DeclarativeMeta]): The entity or table that should be checked.
    """
    table = as_table(sa_obj)
    if len(
        hypertable_partition_columns := get_typed_columns(HypertablePartition, sa_obj)
    ):
        logger.info(
            f"Creating hypertable partition using column {hypertable_partition_columns}."
        )
        conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        schema = table.schema or "public"
        conn.execute(
            sa.select(
                sa.text(
                    f"create_hypertable('{schema}.{table.name}', '{hypertable_partition_columns[0]}')"
                )
            )
        )
