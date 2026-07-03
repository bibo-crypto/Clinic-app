"""Settings controller."""

from database.db import get_session
from models.setting import Setting


def get() -> Setting | None:
    session = get_session()
    try:
        s = session.query(Setting).first()
        if s:
            session.expunge(s)
        return s
    finally:
        session.close()


def save(data: dict) -> bool:
    session = get_session()
    try:
        s = session.query(Setting).first()
        if not s:
            s = Setting()
            session.add(s)
        for key, value in data.items():
            setattr(s, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
