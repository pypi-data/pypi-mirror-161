from uuid import uuid4

import pytest
from fin_data.database.load import DBLoader
from fin_data.database.utils import to_safe_snake_case

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db_loader(table, engine):
    async def create_db_loader(**kwargs):
        all_disabled = {
            "sa_obj": table,
            "on_duplicate_key_update": False,
            "row_batch_size": None,
            "remove_duplicate_keys": False,
            "drop_rows_missing_key": False,
            "batch_by_names_present": False,
            # column name filters.
            "drop_names": None,
            "name_to_name": None,
            "name_converter": None,
            "name_to_name_converter": None,
            # column value filters.
            "value_to_value": None,
            "name_to_value": None,
            "value_converter": None,
            "name_to_value_converter": None,
            "drop_values": None,
            "name_to_drop_values": None,
            "drop_on_type_conversion_fail": True,
        }
        kwargs = {**all_disabled, **kwargs}
        return await DBLoader.create(**kwargs, async_engine=engine)

    return create_db_loader


def test_standard_column_name_conversion():
    converted_names = {
        " two   Words  ": "two_words",
        "Multi_Word_Column": "multi_word_column",
        "multiWordColumn": "multi_word_column",
        "MultiWord Column": "multi_word_column",
        "99things": "_99things",
    }
    for k, v in converted_names.items():
        assert to_safe_snake_case(k) == v


async def test_drop_rows_missing_key(db_loader):
    u = await db_loader(drop_rows_missing_key=True)
    rows = [{str(uuid4()): str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert not len(rows)


async def test_name_to_name(db_loader):
    column_name_map_from = str(uuid4())
    u = await db_loader(name_to_name={column_name_map_from: "column"})
    rows = [{column_name_map_from: str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" in rows[0]


async def test_drop_non_table_columns(db_loader):
    u = await db_loader()
    column = str(uuid4())
    rows = [{column: str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert column not in rows[0]


async def test_remove_duplicate_keys(table, random_rows, db_loader):
    rows = random_rows(table, 5)

    n_dupes = 2
    rows += rows[:n_dupes]

    u = await db_loader(remove_duplicate_keys=True)
    filtered_rows = u._remove_duplicate_keys(rows)
    assert len(filtered_rows) == len(rows) - n_dupes


async def test_name_converter(db_loader):
    u = await db_loader(name_converter=lambda v: v + "n")
    rows = [{"colum": str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" in rows[0]


async def test_column_name_converter(db_loader):
    u = await db_loader(name_to_name_converter={"colum": lambda v: v + "n"})
    rows = [{"colum": str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" in rows[0]


async def test_drop_names(db_loader):
    u = await db_loader(drop_names=["column"])
    rows = [{"column": str(uuid4())}]
    for func in u.filters.values():
        rows = func(rows)
    assert "column" not in rows[0]


async def test_value_to_value(db_loader):
    u = await db_loader(value_to_value={"map_from": "map_to"})
    rows = [{"column": "map_from"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert rows[0]["column"] == "map_to"


async def test_name_to_value(db_loader):
    u = await db_loader(name_to_value={"column": "value"})
    rows = [{"column": "not_value"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert rows[0]["column"] == "value"


async def test_value_converter(db_loader):
    u = await db_loader(value_converter=lambda v: v + v)
    rows = [{"column": "value"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert rows[0]["column"] == "valuevalue"


async def test_name_to_value_converter(db_loader):
    u = await db_loader(name_to_value_converter={"column": lambda v: v + v})
    rows = [{"column": "value"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert rows[0]["column"] == "valuevalue"


async def test_drop_values(db_loader):
    # Values where columns should be dropped if they are that value. (e.g ['null', None, 'Na']). Defaults to None.
    u = await db_loader(drop_values=["null"])
    rows = [{"column": "null"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" not in rows[0]


async def test_name_to_drop_values(db_loader):
    u = await db_loader(name_to_drop_values={"column": "null"})
    rows = [{"column": "null"}]
    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" not in rows[0]


async def test_drop_on_type_conversion_fail(db_loader):
    def conveter(value):
        raise RuntimeError

    rows = [{"column": str(uuid4())}]

    u = await db_loader(value_converter=conveter, drop_on_type_conversion_fail=True)

    for func in u.filters.values():
        rows = func(rows)
    assert len(rows) == 1
    assert "column" not in rows[0]


async def test_raise_on_type_conversion_fail(db_loader):
    def conveter(value):
        raise RuntimeError

    rows = [{"column": str(uuid4())}]

    u = await db_loader(value_converter=conveter, drop_on_type_conversion_fail=False)
    with pytest.raises(RuntimeError):
        for func in u.filters.values():
            rows = func(rows)
