from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv


# ==================================================
# PATH CONFIGURATION
# ==================================================

# Current file:
#
# D:/workspace/chatbot_va/backend/alembic/env.py
#
# backend directory:
#
# D:/workspace/chatbot_va/backend
#
# project root:
#
# D:/workspace/chatbot_va

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROJECT_ROOT = os.path.dirname(
    BACKEND_DIR
)


# ==================================================
# PYTHON PATH
# ==================================================

# Add project root so imports like:
#
# from backend.db.models import Base
#
# work correctly.

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

# .env is located at:
#
# D:/workspace/chatbot_va/backend/.env

ENV_FILE = os.path.join(
    BACKEND_DIR,
    ".env"
)

load_dotenv(
    ENV_FILE
)


# ==================================================
# IMPORT DATABASE MODELS
# ==================================================

from backend.db.models import Base


# ==================================================
# ALEMBIC CONFIG
# ==================================================

config = context.config


# ==================================================
# LOGGING
# ==================================================

if config.config_file_name is not None:

    fileConfig(
        config.config_file_name
    )


# ==================================================
# SQLALCHEMY METADATA
# ==================================================

target_metadata = Base.metadata


# ==================================================
# DATABASE URL
# ==================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)

if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL environment variable is not set"
    )


# Use the DATABASE_URL from backend/.env
# instead of the placeholder in alembic.ini.

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace(
        "%",
        "%%"
    )
)


# ==================================================
# OFFLINE MIGRATIONS
# ==================================================

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():

        context.run_migrations()


# ==================================================
# ONLINE MIGRATIONS
# ==================================================

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():

            context.run_migrations()


# ==================================================
# RUN MIGRATIONS
# ==================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()