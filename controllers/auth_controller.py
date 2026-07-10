"""Authentication controller."""

import bcrypt
from database.db import get_session
from database.first_run import write_password_file
from models.user import User


def verify_reset_token(provided_token: str) -> bool:
    """Validate the setup-generated reset token from the password file."""
    from database.first_run import get_password_file_path

    file_path = get_password_file_path()
    if not file_path.exists():
        return False

    for line in file_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Reset Token :"):
            return line.split(":", 1)[1].strip() == provided_token
    return False


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


def reset_password(username: str, new_password: str, reset_token: str | None = None) -> bool:
    """Reset a user's password and persist the new password to a text file."""
    if not username or not new_password:
        return False
    if reset_token is None or not verify_reset_token(reset_token):
        return False

    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if not user:
            return False

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user.password_hash = hashed
        session.add(user)
        session.commit()
        write_password_file(username, new_password)
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
