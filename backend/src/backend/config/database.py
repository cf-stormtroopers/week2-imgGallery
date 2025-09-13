from sqlmodel import SQLModel, create_engine, Session, select
from backend.config import settings
from typing import Generator

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=False,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=300,     # Recycle connections every 5 minutes
)


def create_db_and_tables():
    """Create database tables."""
    print("Creating database tables...")
    print(engine.url)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session

