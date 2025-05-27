from typing import Any
from uuid import UUID, uuid4

from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from psycopg_pool import ConnectionPool
from psycopg_pool.pool_async import AsyncConnectionPool
from sqlalchemy import Engine, MetaData, create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import config

load_dotenv()


def setup_database() -> Engine:
    engine = create_engine(
        f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
        f'{"" if not config.DB_USE_SSL else "?sslmode=require"}',
        pool_size=config.DB_POOL_SIZE,
        max_overflow=config.DB_MAX_OVERFLOW,
    )

    # Check if vector extension is installed once with lock to avoid race
    # condition
    with engine.connect() as connection:
        connection.execute(text("SELECT pg_advisory_lock(123456)"))
        try:
            result = connection.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            if not result.scalar():
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                connection.commit()
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(123456)"))

    return engine


class ConnectionProvider:
    @staticmethod
    def session() -> sessionmaker:
        return SessionLocal

    @staticmethod
    def psycopgpool() -> ConnectionPool:
        """Creates and returns a psycopg connection pool."""
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        pool = ConnectionPool(
            conninfo=ConnectionProvider.connection_url(),
            max_size=config.DB_POOL_SIZE,
            kwargs=connection_kwargs,
        )
        return pool

    @staticmethod
    def async_psycopgpool() -> AsyncConnectionPool:
        """Creates and returns an async psycopg connection pool."""
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        pool = AsyncConnectionPool(
            conninfo=ConnectionProvider.connection_url(),
            max_size=config.DB_ASYNC_POOL_SIZE,
            kwargs=connection_kwargs,
        )
        return pool

    @staticmethod
    def connection_url() -> str:
        conninfo = (
            f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}"
            f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
        )
        if config.DB_USE_SSL:
            conninfo += "?sslmode=require"
        return conninfo


engine = setup_database()

metadata = MetaData()
Base = declarative_base(metadata=metadata)
SessionLocal: sessionmaker = sessionmaker(engine)


try:
    with engine.connect() as connection:
        print("Connection to DB successful!")
except Exception as e:
    raise Exception("Failed to connect to DB") from e


@event.listens_for(engine, "connect")
def connect(dbapi_connection: Any, _: Any) -> None:
    register_vector(dbapi_connection, arrays=True)


def db_session() -> sessionmaker:
    return SessionLocal


def uuid() -> UUID:
    return uuid4()
