

def most_recent_quotes(symbol: Optional[str] = None):
    if symbol:
        dtq = (
            sa.select(
                sa.func.max(td_option_quotes.c.download_time).label("download_time")
            )
            .where(td_option_quotes.c.u_symbol == symbol)
            .cte("dt_query")
        )
        query = sa.select(td_option_quotes).where(
            td_option_quotes.c.download_time == dtq.c.download_time
        )
        return query
    
    # find most recent quote time for each unique symbol.
    last_quote_times = (
        sa.select(td_option_quotes.c.u_symbol, td_option_quotes.c.download_time)
        .distinct(td_option_quotes.c.u_symbol)
        .order_by(td_option_quotes.c.u_symbol, td_option_quotes.c.download_time.asc())
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
                    last_quote_times.c.download_time == td_option_quotes.c.download_time,
                    last_quote_times.c.u_symbol == td_option_quotes.c.u_symbol,
                ),
            )
        )
        .compile(dialect=postgresql.dialect())
    )
    return query
