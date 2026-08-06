import os
import sys
import logging
from logging.config import fileConfig
import sqlalchemy as sa
from alembic import context

# Ensure app directory is in Python path for import resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Import app components directly to fetch database credentials and metadata
from app.config import get_config
from app.database import Base
from app.models import (  # noqa: F401
    user, organization, org_member, candidate, resume,
    interviewer, interview, interview_score,
    interview_report, availability_slot, notification,
    mock_interview, practice_question,
)

# Fetch current config and ensure database URL has the correct postgresql:// prefix
cfg = get_config()
database_url = cfg.SQLALCHEMY_DATABASE_URI
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

target_metadata = Base.metadata

# Set database URL dynamically in alembic config
config.set_main_option('sqlalchemy.url', database_url)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Use standard SQLAlchemy engine for connection
    connectable = sa.create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
