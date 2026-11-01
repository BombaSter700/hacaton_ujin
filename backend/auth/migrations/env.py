from logging.config import fileConfig

from alembic import context
from app.core.config import settings
from app.core.database.engine import engine
from app.models import Base

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

if context.is_offline_mode():
    context.configure(
        url=settings.database_url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
