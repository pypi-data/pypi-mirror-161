import random
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
import sqlalchemy as sa
from fin_data.blacklist import blacklist_table
from fin_data.database import SourcesDBLoader, as_table
from fin_data.models import company as comp
from fin_data.models.options import top_option_symbols_table
from ready_logger import logger
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql import Select
from symbol_parser import Symbol


def symbols_query(
    in_sources: List[str] = None,
    not_in_sources: List[str] = None,
    row_id_column: str = "data_id",
):
    queries = []
    for t in (comp.CIK, comp.Name):
        table = as_table(t)
        src_table = SourcesDBLoader.get_sources_table(table, row_id_column)
        query = (
            sa.select(t.asset_id)
            .select_from(t)
            .join(src_table, src_table.c.data_id == t.data_id)
            .where(t.asset_id_type == comp.CompanyIDType.SYMBOL)
        )
        if in_sources:
            query = query.where(src_table.c.source.in_(in_sources))
        if not_in_sources:
            query = query.where(src_table.c.source.notin_(not_in_sources))
        queries.append(query)
    return sa.union(*queries)


async def get_symbols(
    engine: AsyncEngine,
    endpoint_name: str = None,
    in_sources: List[str] = None,
    not_in_sources: List[str] = None,
    include_top_options: bool = True,
):
    async with engine.begin() as conn:
        result = await conn.execute(symbols_query(in_sources, not_in_sources))
        symbols = set(result.scalars())
        if include_top_options:
            result = await conn.execute(
                sa.select(top_option_symbols_table.c.symbol.distinct())
            )
            symbols.update(result.scalars())
        symbols = {Symbol(s).base_symbol for s in symbols}
        logger.info(f"Selected {len(symbols)} total symbols from database.")
        if endpoint_name:
            # check is this endpoint has blacklisted symbols.
            bad_symbols_query = (
                sa.select(blacklist_table.c.symbol)
                .select_from(blacklist_table)
                .where(blacklist_table.c.endpoint == endpoint_name)
            )
            result = await conn.execute(bad_symbols_query)
            bad_symbols = list(result.scalars())
            # remove all blacklisted symbols.
            symbols.difference_update(bad_symbols)
            logger.info(
                f"Removing {len(bad_symbols)} blacklisted symbols. {len(symbols)} symbols remain."
            )
    return symbols


def symbols_least_recent_order_query(
    symbol_column: sa.Column, time_column: sa.Column
) -> Select:
    # TODO does this work with joined tables?
    """

    Args:
        symbol_column (sa.Column): [description]
        time_column (sa.Column): [description]

    Returns:
        Select: [description]
    """
    query = (
        sa.select(sa.column("symbol"))
        .select_from(
            sa.select(symbol_column, time_column)
            .distinct(symbol_column)
            .order_by(symbol_column, time_column.desc())
            .subquery()
        )
        .order_by(time_column.desc())
        .compile(dialect=postgresql.dialect())
    )
    return query


async def all_symbols_priority_order(
    engine: AsyncEngine,
    processed_symbols_column: sa.Column,
    processed_symbols_time_column: sa.Column,
    symbols_query: Select,
):
    async with engine.begin() as conn:
        processed_symbols = await conn.execute(
            symbols_least_recent_order_query(
                processed_symbols_column, processed_symbols_time_column
            )
        ).scalars()
        processed_symbols = list(processed_symbols)
        symbols_query = symbols_query.where(
            sa.columns("asset_id").notin_(processed_symbols)
        )
        new_symbols = list(conn.execute(symbols_query).scalars())
    random.shuffle(new_symbols)
    # make sure unprocessed symbols run first, then run in order of least recently processed.
    logger.info(
        f"Found {len(processed_symbols)} processed symbols, {len(new_symbols)} new symbols."
    )
    return new_symbols + processed_symbols


async def find_new_entities_query(
    sa_obj: Union[sa.Table, DeclarativeMeta],
    since_time: datetime,
    sources: Optional[Union[List[str], str]] = None,
) -> Select:
    """Find entities that were recently inserted added to the database.

    Args:
        sa_obj (Union[sa.Table, DeclarativeMeta]): The entity to check for new instances of.
        since_time (Union[datetime, str]): Oldest time that should be considered 'new'.
        count (bool, optional): Return number of entities instead of entity data rows. Defaults to False.
        source (Optional[str], optional): Restrict the query to a single source. Defaults to None.

    Returns:
        Select: the constructed query.
    """
    table = as_table(sa_obj)
    src_table = SourcesDBLoader.get_sources_table(table)
    if isinstance(sources, str):
        sources = [sources]
    elif sources is None:
        sources = []
    query = (
        sa.select(sa_obj)
        .select_from(table)
        .join(src_table, src_table.c.data_id == table.c.data_id)
        .where(src_table.c.created <= since_time)
    )
    if sources:
        query = query.where(src_table.c.source.in_(sources))
    return query


def calculate_avg_volume(
    table: sa.Table,
    engine: Engine,
    period: str = "day",
    min_volume: Optional[int] = None,
) -> pd.DataFrame:
    """Use data in the table to calculate average volume for each symbol for a given period.

    Args:
        table (sa.Table): Table with volume and datetime columns.
        engine (Engine): The engine to use to execute the query.
        period (str, optional): Period to calculate average volume for. Possible options: hour, day, week, month, quarter, year. Defaults to 'day'.
        min_volume (Optional[int], optional): Only return data for symbols that have at least this average volume. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with symbols and average volume.
    """
    avg_volume = sa.func.sum(table.c.volume) / sa.func.count(
        # TODO use index?
        sa.func.distinct(sa.func.date_trunc(period, table.c.datetime))
    )
    query = (
        sa.select(table.c.symbol, avg_volume.label("avg_vol"))
        .select_from(table)
        .group_by(table.c.symbol)
        .order_by("avg_vol")
    )
    if min_volume is not None:
        query = query.having(avg_volume > min_volume)
    return pd.read_sql_query(query, engine)


def most_recent_quotes():
    # TODO table/cols args.
    # find most recent quote time for each unique symbol.
    last_quote_times = (
        sa.select(td_option_quotes.c.u_symbol, td_option_quotes.c.quote_time)
        .distinct(td_option_quotes.c.u_symbol)
        .order_by(td_option_quotes.c.u_symbol, td_option_quotes.c.quote_time.asc())
        .subquery()
    )
    # self-join to all rows that have the symbol and it's most recent quote time.
    # compile with PostgreSQL dialect to generate the SELECT DISTINCT ON query.
    query = (
        sa.select(td_option_quotes)
        .select_from(
            last_quote_times.outerjoin(
                td_option_quotes,
                sa.and_(
                    last_quote_times.c.quote_time == td_option_quotes.c.quote_time,
                    last_quote_times.c.u_symbol == td_option_quotes.c.u_symbol,
                ),
            )
        )
        .compile(dialect=postgresql.dialect())
    )
    return query


REGISTRY = {
    "all_symbols_priority_order": all_symbols_priority_order,
}
