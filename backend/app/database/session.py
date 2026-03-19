import os
import sys
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

# Import models to register them with SQLModel metadata

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Require PostgreSQL database - no SQLite fallback in production
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!", file=sys.stderr)
    print("Please set DATABASE_URL to your Neon PostgreSQL connection string.", file=sys.stderr)
    print("Get your connection string from: https://console.neon.tech/", file=sys.stderr)
    sys.exit(1)

if DATABASE_URL.startswith("sqlite"):
    print("ERROR: SQLite is not supported in production. Please use PostgreSQL.", file=sys.stderr)
    sys.exit(1)

print(f"Using PostgreSQL database: {DATABASE_URL.split('@')[1].split('?')[0] if '@' in DATABASE_URL else '***'}")


# Create engine with proper connection pooling for Neon PostgreSQL
# Neon PostgreSQL configuration with serverless connections
# Use NullPool to avoid connection pooling issues with serverless DBs
# sslmode is already in the DATABASE_URL, no need to add it again
engine_kwargs = {
    "poolclass": NullPool,
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_recycle": 300,  # Recycle connections after 5 minutes
}

engine = create_engine(DATABASE_URL, **engine_kwargs)


def create_db_and_tables():
    """Create database tables"""
    # Create all tables defined in the models
    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
