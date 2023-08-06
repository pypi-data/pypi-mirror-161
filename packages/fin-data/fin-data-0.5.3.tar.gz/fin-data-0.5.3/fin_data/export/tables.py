from datetime import datetime

import sqlalchemy as sa

metadata = sa.MetaData(schema="exports")

table_export_size_table = sa.Table(
    "table_export_size",
    metadata,
    sa.Column("table", sa.String, primary_key=True, comment="Format: {schema}.{table}"),
    sa.Column(
        "export_row_count",
        sa.Integer,
        nullable=False,
        comment="Desired number of rows to export per file.",
    ),
)


tables_exports_table = sa.Table(
    "table_exports",
    metadata,
    sa.Column("file", sa.String, primary_key=True),
    sa.Column("file_start", sa.DateTime(timezone=False)),
    sa.Column("file_end", sa.DateTime(timezone=False)),
    sa.Column("row_count", sa.Integer, nullable=False),
    sa.Column("table", sa.String, nullable=False, comment="Format: {schema}.{table}"),
    sa.Column(
        "updated", sa.DateTime(timezone=False), default=datetime.utcnow, nullable=False
    ),
)

symbol_exports_table = sa.Table(
    "symbol_exports",
    metadata,
    sa.Column("file", sa.String, primary_key=True),
    sa.Column("file_start", sa.DateTime(timezone=False), nullable=False, index=True),
    sa.Column("file_end", sa.DateTime(timezone=False), nullable=False),
    sa.Column("row_count", sa.Integer, nullable=False),
    sa.Column(
        "table",
        sa.String,
        nullable=False,
        index=True,
        comment="Format: {schema}.{table}",
    ),
    sa.Column("symbol", sa.String, nullable=False, index=True),
    sa.Column(
        "updated", sa.DateTime(timezone=False), default=datetime.utcnow, nullable=False
    ),
)
