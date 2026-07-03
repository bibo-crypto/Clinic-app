"""User model for authentication and role management."""

from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="receptionist")  # admin, doctor, receptionist
    is_active = Column(Boolean, default=True)
