import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Optional, Union

import pandas as pd
import sqlalchemy as sa
from fin_data.database.engine import engine_from_env
from fin_data.s3 import df_from_s3
from ready_logger import get_logger
from sqlalchemy.engine import Engine

from .tables import symbol_exports_table, table_export_size_table

logger = get_logger("fin-data-exports")


def schema_table(table: sa.Table) -> str:
    return f"{table.schema or 'public'}.{table.name}"


def determine_export_row_count(
    table: sa.Table,
    conn,
    export_size_mb: Optional[int] = 100,
    sample_size: int = 50_000,
) -> int:
    logger.info(f"Determining export row count for table {table.name}...")
    sample = pd.read_sql_query(sa.select(table).limit(sample_size), conn)
    sample_file = NamedTemporaryFile().name
    sample.to_parquet(sample_file)
    sample_mb = os.path.getsize(sample_file) / 10**6
    logger.info(
        f"Created {sample.shape} sample file for table {table.name} ({sample_mb}mb)."
    )
    export_row_count = round((export_size_mb / sample_mb) * sample_size)
    logger.info(f"Determined export row count: {export_row_count}.")
    conn.execute(
        sa.insert(table_export_size_table).values(
            {
                "table": schema_table(table),
                "export_row_count": export_row_count,
            }
        )
    )
    return export_row_count


def get_symbol_file(
    symbol: str,
    since: Optional[Union[str, datetime]] = None,
    engine: Optional[Engine] = None,
) -> pd.DataFrame:
    engine = engine or engine_from_env()
    query = (
        sa.select(symbol_exports_table.c.file)
        .where(symbol_exports_table.c.symbol == symbol)
        .order_by(symbol_exports_table.c.file_end)
    )
    if since:
        query = query.where(
            symbol_exports_table.c.file.notin_(
                sa.select(symbol_exports_table.c.file)
                .where(symbol_exports_table.c.file_end < since)
                .subquery()
            )
        )
    with engine.begin() as conn:
        files = list(conn.execute(query).scalars())
    return df_from_s3(files)
