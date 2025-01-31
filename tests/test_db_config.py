from sqlalchemy.orm import Session

from core.db.config import get_db


def test_get_db():
    db = next(get_db())
    assert isinstance(db, Session)
    db.close()
