"""
Database initialization and session management.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from utils.paths import get_runtime_data_dir

# Database file location
DATA_DIR = get_runtime_data_dir()
DB_DIR = DATA_DIR / "database"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = str(DB_DIR / "clinic.db")
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
    _ensure_invoice_columns()
    _seed_defaults()


def _ensure_invoice_columns():
    """Add missing invoice columns for older databases."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "invoices" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("invoices")}
    if "doctor_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE invoices ADD COLUMN doctor_id INTEGER"))


def _seed_defaults():
    """Seed default admin user and settings if not present."""
    import bcrypt
    from models.user import User
    from models.setting import Setting

    session = get_session()
    try:
        from database.first_run import ensure_setup_credentials, get_password_file_path

        credentials = ensure_setup_credentials("admin")
        admin_user = session.query(User).filter_by(username="admin").first()

        if not admin_user:
            hashed = bcrypt.hashpw(str(credentials["password"]).encode(), bcrypt.gensalt()).decode()
            admin_user = User(username="admin", password_hash=hashed, role="admin", full_name="Administrator")
            session.add(admin_user)
        else:
            password_file = get_password_file_path()
            reset_file = password_file.with_name("ClinicSystem_RESET_PASSWORD.txt")
            if not password_file.exists() or not reset_file.exists():
                hashed = bcrypt.hashpw(str(credentials["password"]).encode(), bcrypt.gensalt()).decode()
                admin_user.password_hash = hashed
                session.add(admin_user)

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
