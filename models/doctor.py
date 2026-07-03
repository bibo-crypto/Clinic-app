"""Doctor model."""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database.db import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    specialization = Column(String(100))
    phone = Column(String(20))
    consultation_fee = Column(Float, default=0.0)

    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
