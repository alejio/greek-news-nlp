"""Database connection configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = DATABASE_URL = (
    f"postgresql+psycopg2://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost/gazzetta"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
