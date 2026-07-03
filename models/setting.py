"""Application settings model."""

from sqlalchemy import Column, Integer, String
from database.db import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clinic_name = Column(String(100), default="My Clinic")
    theme = Column(String(10), default="light")
    language = Column(String(5), default="en")
    logo_path = Column(String(300), default="")
