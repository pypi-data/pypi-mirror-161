from uuid import uuid4

import sqlalchemy as sa
from fin_data.database import compare
from sqlalchemy.dialects import postgresql


def test_is_same_column_type():
    sa_pg_types = [
        # test dialect types.
        (sa.Boolean, postgresql.BOOLEAN),
        (sa.String, postgresql.VARCHAR),
        (sa.SmallInteger, postgresql.SMALLINT),
        (sa.BigInteger, postgresql.BIGINT),
        (sa.DateTime, postgresql.TIMESTAMP),
        (sa.Float, postgresql.FLOAT),
        (sa.Float, postgresql.DOUBLE_PRECISION),
        (sa.Integer, postgresql.INTEGER),
        (sa.Time, postgresql.TIME),
        # test type parameters.
        (sa.Numeric, postgresql.NUMERIC),
    ]
    for t1, t2 in sa_pg_types:
        assert compare.is_same_col_type(
            sa.Column(str(uuid4()), t1), sa.Column(str(uuid4()), t2)
        )
    assert compare.is_same_col_type(
        sa.Column(str(uuid4()), sa.Enum("A", "B")),
        sa.Column(str(uuid4()), sa.Enum("A", "B")),
    )
    assert not compare.is_same_col_type(
        sa.Column(str(uuid4()), sa.Enum("A", "B")),
        sa.Column(str(uuid4()), sa.Enum("C", "B")),
    )


def test_column_type_mismatch(table):
    mm = compare.column_type_mismatch(table, table)
    assert not len(mm)

    table2 = sa.Table(
        str(uuid4()),
        sa.MetaData(),
        # column is in table fixture is sa.String.
        sa.Column("column", sa.Integer),
    )
    mm = compare.column_type_mismatch(table, table2)
    assert len(mm) == 1


def test_column_name_mismatch(table):
    # check match.
    db_cols_not_in_sa, sa_cols_not_in_db = compare.column_name_mismatch(
        sa_obj=table, reflected_table=table
    )
    assert not len(db_cols_not_in_sa)
    assert not len(sa_cols_not_in_db)
    # check not match.
    table2 = sa.Table(
        str(uuid4()),
        sa.MetaData(),
        # use column with new name.
        sa.Column(str(uuid4()), sa.String),
    )
    db_cols_not_in_sa, sa_cols_not_in_db = compare.column_name_mismatch(
        sa_obj=table, reflected_table=table2
    )
    assert len(db_cols_not_in_sa) == 1
    assert len(sa_cols_not_in_db) == 1


def test_nullable_column_mismatch(table):
    # check match.
    db_nullable_not_in_sa, sa_nullable_not_in_db = compare.nullable_column_mismatch(
        sa_obj=table, reflected_table=table
    )
    assert not len(db_nullable_not_in_sa)
    assert not len(sa_nullable_not_in_db)
    # check not match.
    table2 = sa.Table(
        str(uuid4()),
        sa.MetaData(),
        sa.Column("column", sa.String, nullable=False),
    )
    db_nullable_not_in_sa, sa_nullable_not_in_db = compare.nullable_column_mismatch(
        sa_obj=table, reflected_table=table2
    )
    assert not len(db_nullable_not_in_sa)
    assert len(sa_nullable_not_in_db) == 1

    db_nullable_not_in_sa, sa_nullable_not_in_db = compare.nullable_column_mismatch(
        sa_obj=table2, reflected_table=table
    )
    assert len(db_nullable_not_in_sa) == 1
    assert not len(sa_nullable_not_in_db)


def test_foreign_key_mismatch(table):
    # check match.
    db_fk_not_in_sa, sa_fk_not_in_db = compare.foreign_key_mismatch(
        sa_obj=table, reflected_table=table
    )
    assert not len(db_fk_not_in_sa)
    assert not len(sa_fk_not_in_db)
    # check not match.
    table2 = sa.Table(
        str(uuid4()),
        sa.MetaData(),
        sa.Column("column", sa.String, sa.ForeignKey(str(uuid4()))),
    )
    db_fk_not_in_sa, sa_fk_not_in_db = compare.foreign_key_mismatch(
        sa_obj=table, reflected_table=table2
    )
    assert len(db_fk_not_in_sa) == 1
    assert not len(sa_fk_not_in_db)

    db_fk_not_in_sa, sa_fk_not_in_db = compare.foreign_key_mismatch(
        sa_obj=table2, reflected_table=table
    )
    assert not len(db_fk_not_in_sa)
    assert len(sa_fk_not_in_db) == 1


def test_primary_key_mismatch(table):
    # check match.
    db_pk_not_in_sa, sa_pk_not_in_db = compare.primary_key_mismatch(
        sa_obj=table, reflected_table=table
    )
    assert not len(db_pk_not_in_sa)
    assert not len(sa_pk_not_in_db)
    # check not match.
    table2 = sa.Table(
        str(uuid4()),
        sa.MetaData(),
        # use non-nullable column.
        sa.Column("column", sa.String, primary_key=True),
    )
    db_pk_not_in_sa, sa_pk_not_in_db = compare.primary_key_mismatch(
        sa_obj=table, reflected_table=table2
    )
    assert len(db_pk_not_in_sa) == 1
    assert not len(sa_pk_not_in_db)

    db_pk_not_in_sa, sa_pk_not_in_db = compare.primary_key_mismatch(
        sa_obj=table2, reflected_table=table
    )
    assert not len(db_pk_not_in_sa)
    assert len(sa_pk_not_in_db) == 1
