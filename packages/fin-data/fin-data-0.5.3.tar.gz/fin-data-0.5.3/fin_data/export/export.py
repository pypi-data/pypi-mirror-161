import os
from datetime import datetime
from multiprocessing import Process, Queue
from pprint import pformat
from typing import Optional, Sequence, Union

import pandas as pd
import sqlalchemy as sa
from fin_data import cached_engine_from_env, engine_from_env
from fin_data.s3 import get_bucket, s3_storage_options, save_parquet
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine

from .tables import symbol_exports_table, table_export_size_table, tables_exports_table
from .utils import determine_export_row_count, logger, schema_table


def _export_row_count(table: sa.Table, engine: Engine) -> int:
    # find how many rows we should export per file.
    with engine.begin() as conn:
        export_row_count = conn.execute(
            sa.select(
                table_export_size_table.c.export_row_count,
            ).where(table_export_size_table.c.table == schema_table(table))
        ).scalar()
        if not export_row_count:
            export_row_count = determine_export_row_count(table, conn)
    return export_row_count


def _run_export(
    bucket: str,
    table: sa.Table,
    export_row_count: int,
    time_column: sa.Column,
    engine: Engine,
    symbol_column: Optional[sa.Column] = None,
    symbol: Optional[str] = None,
    archive: bool = False,
):
    if symbol_column is None and symbol is not None:
        raise ValueError("`symbol_column` must be provided when exporting symbol data.")

    # export metadata table.
    exports_table = symbol_exports_table if symbol else tables_exports_table

    logger.info(
        f"Exporting table {table.name} to {export_row_count} row files. Saving files to bucket {bucket}."
    )
    data_select = sa.select(table).order_by(time_column.asc())
    if symbol:
        data_select = data_select.where(symbol_column == symbol)
    with engine.begin() as conn:
        # check if parts of the table have already been exported.
        last_export_file_end = sa.select(sa.func.max(exports_table.c.file_end))
        last_export_query = sa.select(
            exports_table.c.file,
            exports_table.c.file_end,
            exports_table.c.row_count,
        )
        if symbol:
            last_export_query = last_export_query.where(
                exports_table.c.symbol == symbol
            )
            last_export_file_end = last_export_file_end.where(
                exports_table.c.symbol == symbol
            )
        last_export_query = last_export_query.where(
            exports_table.c.file_end == last_export_file_end.scalar_subquery()
        )
        if last_export := conn.execute(last_export_query).fetchone():
            (
                last_export_file,
                last_export_end,
                last_export_row_count,
            ) = last_export
            # check if last export file is smaller than desired size.
            if (rows_remaining := (export_row_count - last_export_row_count)) > 0:
                # append more rows to last file.
                export_p2 = pd.read_sql_query(
                    data_select.where(time_column > last_export_end).limit(
                        rows_remaining
                    ),
                    conn,
                )
                if n_export_p2_rows := len(export_p2):
                    logger.info(
                        f"Last export for {symbol or table.name} was {rows_remaining} rows less than the desired {export_row_count}. Appended {n_export_p2_rows} rows."
                    )
                    storage_options = s3_storage_options()
                    # load old export file so we can append to it.
                    export_p1 = pd.read_parquet(
                        last_export_file, storage_options=storage_options
                    )
                    export = pd.concat([export_p1, export_p2])
                    # update new last export end time to account for newly added data.
                    last_export_end = export_p2[time_column.name].max()
                    # save new file with updated data.
                    export.to_parquet(last_export_file, storage_options=storage_options)
                    meta = {
                        "file_end": last_export_end,
                        "row_count": len(export),
                        "updated": datetime.utcnow(),
                    }
                    logger.info(f"Updating export meta:\n{pformat(meta)}")
                    conn.execute(
                        sa.update(exports_table)
                        .where(exports_table.c.file == last_export_file)
                        .values(meta)
                    )
            else:
                logger.info(
                    "Last export file is desired size. Will not append more data."
                )
            # select everything since last export.
            logger.info(f"Selecting data since last export: {last_export_end}")
            data_select = data_select.where(time_column > last_export_end)
        else:
            last_export_end = None
    # start next export.
    with engine.connect().execution_options(stream_results=True) as conn:
        for export in pd.read_sql_query(data_select, conn, chunksize=export_row_count):
            if not len(export):
                break
            file_end = export[time_column.name].max()
            file_start = last_export_end or export[time_column.name].min()
            file = save_parquet(
                export,
                bucket=bucket,
                table=table,
                symbol=symbol,
                archive=archive,
                file_start_time=file_start,
            )
            meta = {
                "file": file,
                "file_start": file_start,
                "file_end": file_end,
                "row_count": len(export),
                "table": schema_table(table),
            }
            if symbol:
                meta["symbol"] = symbol
            logger.info(f"Finished export:\n{pformat(meta)}")
            with engine.begin() as iconn:
                iconn.execute(sa.insert(exports_table).values(meta))
            last_export_end = file_end


def _export_symbols_worker(symbols_q, export_kwargs):
    pid = os.getpid()
    while symbols_q.qsize():
        symbol = symbols_q.get()
        logger.info(f"[{pid}] Exporting data for symbol {symbol}.")
        _run_export(symbol=symbol, **export_kwargs)


def export_table(
    bucket: str, table: sa.Table, archive: bool = False, engine: Optional[Engine] = None
) -> str:
    """Export an entire table to a single parquet file.

    Args:
        engine (Engine): Engine to use to select the data.
        table (sa.Table): The table to export.

    Returns:
        str: Path to the exported file.
    """
    get_bucket(bucket)
    engine = engine or cached_engine_from_env()
    df = pd.read_sql_query(sa.select(table), engine)
    logger.info(f"Exporting table {table.name} {df.shape}. Saving to bucket {bucket}.")
    file = save_parquet(df, bucket, table, archive=archive)
    meta = {
        "file": file,
        "row_count": len(df),
        "table": schema_table(table),
    }
    statement = (
        postgresql.insert(tables_exports_table)
        .values(meta)
        .on_conflict_do_update(
            index_elements=["file"],
            set_={"row_count": meta["row_count"], "table": meta["table"]},
        )
    )
    with engine.begin() as conn:
        conn.execute(statement)
    return file


def export_time_slices(
    bucket: str,
    table: sa.Table,
    time_column: sa.Column,
    archive: bool = False,
    trim: bool = False,
    engine: Optional[Engine] = None,
):
    logger.info(
        f"Exporting time slices from table {table.name}. Saving to bucket {bucket}."
    )
    # make sure bucket exists.
    get_bucket(bucket)
    engine = engine or cached_engine_from_env()
    _run_export(
        bucket=bucket,
        table=table,
        export_row_count=_export_row_count(table, engine),
        time_column=time_column,
        archive=archive,
        engine=engine,
    )
    if trim:
        trim_exported_table(
            table,
            time_column,
            engine,
        )



def export_symbols(
    bucket: str,
    table: sa.Table,
    time_column: sa.Column,
    symbol_column: sa.Column,
    symbols: Optional[Union[str, Sequence[str]]] = None,
    trim: bool = False,
    n_proc: int = 1,
):
    engine = engine_from_env()
    symbols_q = Queue()
    if isinstance(symbols, str):
        symbols_q.put(symbols)
    else:
        if symbols is None:
            # export all unique symbols in table.
            with engine.begin() as conn:
                symbols = list(
                    conn.execute(
                        sa.select(symbol_column.distinct()).select_from(table)
                    ).scalars()
                )
        for s in symbols:
            symbols_q.put(s)

    # make sure bucket exists.
    get_bucket(bucket)
    export_row_count = _export_row_count(table, engine)
    logger.info(
        f"Exporting data for {symbols_q.qsize()} symbols. Saving to bucket {bucket}."
    )
    export_kwargs = {
        "bucket": bucket,
        "table": table,
        "export_row_count": export_row_count,
        "time_column": time_column,
        "engine": engine,
        "symbol_column": symbol_column,
    }
    if n_proc == 1 or symbols_q.qsize() == 1:
        _export_symbols_worker(symbols_q, export_kwargs)
    else:
        # don't pass open connection through process boundries.
        engine.dispose()
        logger.info(f"Starting {n_proc} symbol export worker processes.")
        procs = [
            Process(
                target=_export_symbols_worker,
                args=(symbols_q, export_kwargs),
            )
            for _ in range(n_proc)
        ]
        for p in procs:
            p.start()
        for p in procs:
            p.join()
    if trim:
        trim_exported_table(
            table,
            time_column,
            engine,
        )


def trim_exported_table(
    table: sa.Table,
    time_column: sa.Column,
    engine: Optional[Engine] = None,
):
    engine = engine or cached_engine_from_env()
    with engine.begin() as conn:
        conn.execute(
            sa.delete(table).where(
                time_column
                <= sa.select(sa.func.max(tables_exports_table.c.file_end))
                .where(tables_exports_table.c.table == schema_table(table))
                .scalar_subquery()
            )
        )
