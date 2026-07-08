"""Authentication controller."""

import bcrypt
from database.db import get_session
from models.user import User


def login(username: str, password: str):
    """
    Attempt login. Returns User object on success, None on failure.
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            # Detach from session so it can be used outside
            session.expunge(user)
            return user
        return None
    finally:
        session.close()


def change_password(user_id: int, current_password: str, new_password: str) -> bool:
    """Change user's password after verifying current password.

    Returns True on success, False if the current password is incorrect.
    Raises on unexpected errors.
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            return False
        if not bcrypt.checkpw(current_password.encode(), user.password_hash.encode()):
            return False
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user.password_hash = hashed
        session.add(user)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
