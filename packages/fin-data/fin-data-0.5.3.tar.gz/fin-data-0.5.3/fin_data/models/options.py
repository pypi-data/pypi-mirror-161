import sqlalchemy as sa

meta = sa.MetaData(schema="options")

top_option_symbols_table = sa.Table(
    "top_option_symbols",
    meta,
    sa.Column("symbol", sa.String, primary_key=True),
)

option_contracts_table = sa.Table(
    "option_contracts",
    meta,
    sa.Column("id", sa.String, primary_key=True, comment="symbol+expiration+strike+put/call"),
    sa.Column("symbol", sa.String),
    sa.Column("underlyingSecType", sa.String, comment='e.g. FOP, FUT, STK, OPT'),
    sa.Column("SecType", sa.String, comment='e.g. FOP, FUT, STK, OPT'),
    sa.Column('underlyingConId', sa.Integer, comment='From IB details.'),
    sa.Column('expiration', sa.DateTime(timezone=False)),
    sa.Column('strike', sa.Float),
    sa.Column('currency', sa.String, default='USD'),
    sa.Column('exchange', sa.String),
    sa.Column('multiplier', sa.Integer, default=100),
)

option_contract_sources = sa.Table(
    "option_contract_sources",
    meta,
    sa.Column("id", sa.String, primary_key=True, comment="symbol+expiration+strike+put/call"),
    sa.Column('source', sa.String),
)
