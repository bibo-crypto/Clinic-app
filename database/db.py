"""
Database initialization and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database file location
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "clinic.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_session():
    """Return a new database session."""
    return SessionLocal()


def init_db():
    """Create all tables and seed default data."""
    from models import user, patient, doctor, appointment, medical_record, invoice, setting  # noqa
    Base.metadata.create_all(bind=engine)
    _seed_defaults()


def _seed_defaults():
    """Seed default admin user and settings if not present."""
    import bcrypt
    from models.user import User
    from models.setting import Setting

    session = get_session()
    try:
        # Default admin user — random password written to Desktop on first run
        if not session.query(User).filter_by(username="admin").first():
            from database.first_run import generate_admin_password
            password = generate_admin_password()
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            admin = User(username="admin", password_hash=hashed, role="admin", full_name="Administrator")
            session.add(admin)

        # Default settings
        if not session.query(Setting).first():
            defaults = Setting(
                clinic_name="My Clinic",
                theme="light",
                language="en",
                logo_path=""
            )
            session.add(defaults)

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Seed error: {e}")
    finally:
        session.close()
