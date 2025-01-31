import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db.models import Base


@pytest.fixture(scope="function")
def test_db():
    """Create a test database and return a session."""
    # Use SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
