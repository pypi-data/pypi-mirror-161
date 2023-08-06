from functools import cache

import sqlalchemy as sa
from pydantic import BaseSettings, PostgresDsn
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine


class PgCfg(BaseSettings):
    url: PostgresDsn
    async_url: PostgresDsn

    class Config:
        env_prefix = 'postgres_'


def engine_from_env() -> Engine:
    """Create an SQLAlchemy engine.

    Returns:
        Engine: The sqlalchemy engine.
    """
    return sa.create_engine(PgCfg().url)


@cache
def cached_engine_from_env() -> Engine:
    """Create an SQLAlchemy engine and cache it so we only create it once.
    The open connections can be closed by: cached_engine_from_env().dispose()

    Returns:
        Engine: The sqlalchemy engine.
    """
    return engine_from_env()


def async_engine_from_env() -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Returns:
        AsyncEngine: The sqlalchemy engine.
    """
    return create_async_engine(PgCfg().async_url)


@cache
def cached_async_engine_from_env() -> AsyncEngine:
    """Create an async SQLAlchemy engine and chache it so we only create it once.

    Returns:
        AsyncEngine: The sqlalchemy engine.
    """
    return async_engine_from_env()
