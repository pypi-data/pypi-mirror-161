from datetime import datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fin_data.database.load import DBLoader
from fin_data.database.load_sources import SourcesDBLoader

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture
async def sources_linked_table(engine, testing_schema):
    table = sa.Table(
        str(uuid4()),
        sa.MetaData(schema=testing_schema),
        sa.Column("data_id", sa.String, primary_key=True),
        sa.Column("column1", sa.String, comment="DataIDIgnore"),
        sa.Column("column2", sa.String),
    )
    async with engine.begin() as conn:
        await conn.run_sync(table.create)
    yield table
    async with engine.begin() as conn:
        await conn.run_sync(table.drop)


@pytest.fixture
async def sources_db_loader(engine, sources_linked_table):
    sources_loader = await SourcesDBLoader.create(
        source="test",
        row_id_column="data_id",
        generate_row_id=True,
        db_loader=await DBLoader.create(sources_linked_table, async_engine=engine),
    )
    yield sources_loader
    async with engine.begin() as conn:
        await conn.run_sync(sources_loader._sources_table.drop)


async def test_upsert(
    engine,
    sources_db_loader,
):
    row = {"column2": str(uuid4())}
    query = sa.select(
        [
            sources_db_loader._sources_table.c.last_seen,
            sources_db_loader._sources_table.c.times_seen,
        ]
    ).where(sources_db_loader._sources_table.c.source == "test")
    for i in range(1, 3):
        t_before_upsert = datetime.utcnow()
        await sources_db_loader.load([row])
        async with engine.begin() as conn:
            res = await conn.execute(query)
            rows = res.fetchall()
        # check that same row was updated instead of inserting new.
        assert len(rows) == 1
        last_seen, times_seen = rows.pop()
        assert last_seen > t_before_upsert
        assert times_seen == i
