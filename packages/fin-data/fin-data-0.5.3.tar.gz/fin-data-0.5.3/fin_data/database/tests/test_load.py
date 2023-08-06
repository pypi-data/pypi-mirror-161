from copy import deepcopy
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fin_data.database.load import DBLoader
from fin_data.database.utils import groupby_columns
from sqlalchemy.exc import CompileError

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


def row_count_query(table):
    return sa.select(sa.func.count(sa.text("*"))).select_from(table)


async def test_rows_load(key_value_table, random_rows, engine):
    """Check that rows load to database."""
    loader = await DBLoader.create(key_value_table, async_engine=engine)
    n_rows = 10
    await loader.load(random_rows(key_value_table, n_rows))
    async with engine.begin() as conn:
        res = await conn.execute(row_count_query(key_value_table))
        db_row_count = res.scalar()
    assert db_row_count == n_rows


async def test_batches_load(key_value_table, random_rows, engine):
    """Check that rows load to database."""
    loader = await DBLoader.create(
        key_value_table, row_batch_size=10, async_engine=engine
    )
    n_rows = 25
    await loader.load(random_rows(key_value_table, n_rows))
    async with engine.begin() as conn:
        res = await conn.execute(row_count_query(key_value_table))
        db_row_count = res.scalar()
    assert db_row_count == n_rows


async def test_rows_buffer(key_value_table, random_rows, engine):
    """Check that rows load to database."""
    loader = await DBLoader.create(key_value_table, async_engine=engine)
    n_rows = 10
    rows = random_rows(key_value_table, n_rows)
    loader.row_buffer.extend(rows)
    await loader.load()
    async with engine.begin() as conn:
        res = await conn.execute(row_count_query(key_value_table))
        db_row_count = res.scalar()
    assert db_row_count == n_rows


async def test_on_dupe_ignore(key_value_table, random_rows, engine):
    loader = await DBLoader.create(
        key_value_table, on_duplicate_key_update=False, async_engine=engine
    )

    n_rows = 10
    rows = random_rows(key_value_table, n_rows)

    # load rows.
    await loader.load(rows)

    n_pkey_to_update = 5
    for row in rows[:n_pkey_to_update]:
        # rows with new key should get inserted.
        row["key"] += str(uuid4())
    for row in rows[n_pkey_to_update:]:
        # rows with same key should be ignore regardless of updated data.
        row["data"] += str(uuid4())
    # check that duplicate rows get ignored without error and new rows get inserted.
    await loader.load(rows)
    async with engine.begin() as conn:
        res = await conn.execute(row_count_query(key_value_table))
        db_row_count = res.scalar()
    assert db_row_count == n_rows + n_pkey_to_update
    local_values_updated = {r["data"] for r in rows[n_pkey_to_update:]}
    local_values_updated_keys = [r["key"] for r in rows[n_pkey_to_update:]]
    # check that duplicate key rows with values that were updated locally do not have their values updated in the database.
    query = sa.select(key_value_table.c.data).where(
        key_value_table.c.key.in_(local_values_updated_keys)
    )
    async with engine.begin() as conn:
        res = await conn.execute(query)
        db_values = set(res.scalars())

    assert not len(db_values.intersection(local_values_updated))


async def test_on_duplicate_key_update_column(
    key_multi_value_table, random_rows, engine
):
    loader = await DBLoader.create(
        key_multi_value_table, on_duplicate_key_update=["data1"], async_engine=engine
    )

    n_rows = 5
    rows = random_rows(key_multi_value_table, n_rows)

    # load original rows.
    await loader.load(rows)

    # update row values.
    updated_rows = deepcopy(rows)
    for row in updated_rows:
        row["data1"] += str(uuid4())
        row["data2"] += str(uuid4())

    # load updated rows.
    await loader.load(updated_rows)

    # check that all rows in database have data1 value updated.
    async with engine.begin() as conn:
        res = await conn.execute(sa.select(key_multi_value_table.c.data1))
        db_data1 = set(res.scalars())
    assert not len(db_data1.intersection([r["data1"] for r in rows]))

    # check that no rows in database have data2 value updated.
    async with engine.begin() as conn:
        res = await conn.execute(sa.select(key_multi_value_table.c.data2))
        db_data2 = set(res.scalars())
    assert not len(db_data2.symmetric_difference([r["data2"] for r in rows]))


async def test_on_duplicate_key_update(key_multi_value_table, random_rows, engine):
    loader = await DBLoader.create(
        key_multi_value_table, on_duplicate_key_update=True, async_engine=engine
    )

    n_rows = 5
    rows = random_rows(key_multi_value_table, n_rows)

    # load original rows.
    await loader.load(rows)

    # update row values.
    updated_rows = deepcopy(rows)
    for row in updated_rows:
        row["data1"] += str(uuid4())
        row["data2"] += str(uuid4())

    # load updated rows.
    await loader.load(updated_rows)

    # check that all rows in database have data1 value updated.
    async with engine.begin() as conn:
        res = await conn.execute(sa.select(key_multi_value_table.c.data1))
        db_data1 = set(res.scalars())
    assert not len(db_data1.intersection([r["data1"] for r in rows]))

    # check that all rows in database have data2 value updated.
    async with engine.begin() as conn:
        res = await conn.execute(sa.select(key_multi_value_table.c.data2))
        db_data2 = set(res.scalars())
    assert not len(db_data2.intersection([r["data2"] for r in rows]))


async def test_batch_by_columns_present(key_multi_value_table, engine):
    loader = await DBLoader.create(
        key_multi_value_table, batch_by_names_present=True, async_engine=engine
    )
    rows = [
        {"key": str(uuid4()), "data1": str(uuid4()), "data2": str(uuid4())},
        {"key": str(uuid4()), "data1": str(uuid4())},
    ]
    groups = list(groupby_columns(rows))
    assert len(groups) == 2
    assert isinstance(groups[0], list)
    assert isinstance(groups[1], list)


async def test_compile_error_message(key_multi_value_table, engine):
    loader = await DBLoader.create(
        key_multi_value_table, batch_by_names_present=False, async_engine=engine
    )
    rows = [
        {"key": str(uuid4()), "data1": str(uuid4()), "data2": str(uuid4())},
        {"key": str(uuid4()), "data1": str(uuid4())},
    ]
    statement = loader._build_statement(rows)
    async with loader.engine.begin() as conn:
        with pytest.raises(
            CompileError,
            match="is explicitly rendered as a boundparameter in the VALUES clause",
        ):
            await conn.execute(statement)
