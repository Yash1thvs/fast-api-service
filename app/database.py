from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

# Database URL format: "postgresql+asyncpg://<username>:<password>@<host>/<database_name>"
DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@34.121.45.231:5432/test"

# Async database connection
database = Database(DATABASE_URL)

# Synchronous SQLAlchemy engine and session for other tasks
engine = create_engine(DATABASE_URL.replace("asyncpg", "psycopg2"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()