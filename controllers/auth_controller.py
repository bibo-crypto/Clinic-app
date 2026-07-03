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
