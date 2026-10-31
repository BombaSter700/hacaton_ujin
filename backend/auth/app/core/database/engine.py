"""Local SQLAlchemy engine and per-request session factory."""

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def create_database_engine(config):
    url = make_url(config.database_url)
    options = {"pool_pre_ping": True, "echo": False}
    if url.get_backend_name() == "sqlite":
        options["connect_args"] = {"check_same_thread": False}
        if url.database in (None, "", ":memory:"):
            options["poolclass"] = StaticPool
    else:
        options.update(
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_timeout=config.db_pool_timeout,
            pool_recycle=config.db_pool_recycle,
        )
    return create_engine(url, **options)


def create_session_factory(database_engine):
    return sessionmaker(bind=database_engine, autocommit=False, autoflush=False)


engine = create_database_engine(settings)
SessionLocal = create_session_factory(engine)
