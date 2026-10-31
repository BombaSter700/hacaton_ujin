import sys

sys.path.append("/app/shared")

from core.database.engine import create_database_engine, create_session_factory
from ..config import settings

# Create database engine with connection pooling
engine = create_database_engine(settings)

# Create session factory
SessionLocal = create_session_factory(engine)
