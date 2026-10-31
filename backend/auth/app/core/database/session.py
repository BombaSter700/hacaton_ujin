"""Session ownership: always close, rollback errors, never implicitly commit."""

from contextlib import contextmanager

from .engine import SessionLocal, engine


@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    with get_db_context() as db:
        yield db


def create_tables():
    # Import registered models only when explicitly asked to create the schema.
    from app.models import session, system_settings  # noqa: F401
    from app.models.user import Base

    Base.metadata.create_all(bind=engine)


def drop_tables():
    from app.models import session, system_settings  # noqa: F401
    from app.models.user import Base

    Base.metadata.drop_all(bind=engine)
