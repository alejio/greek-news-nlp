import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.db.models import Base


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["POSTGRES_PASSWORD"] = "test_password"


@pytest.fixture(scope="function")
def test_db() -> Session:
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


@pytest.fixture(scope="function")
def override_get_db(test_db: Session):
    """Override the get_db dependency for testing."""
    try:
        yield test_db
    finally:
        test_db.close()
