"""Patient model."""

from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import relationship
from database.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(10))
    date_of_birth = Column(Date)
    phone = Column(String(20))
    address = Column(String(200))
    blood_type = Column(String(5))
    allergies = Column(Text, default="")
    medical_notes = Column(Text, default="")

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="patient", cascade="all, delete-orphan")
