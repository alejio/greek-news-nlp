import pytest
from data_collection.db.db_config import get_db
from sqlalchemy.orm import Session


def test_get_db():
    db = next(get_db())
    assert isinstance(db, Session)
    db.close()
