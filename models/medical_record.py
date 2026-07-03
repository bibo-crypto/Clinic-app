"""Medical Record model."""

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base
import datetime


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date = Column(Date, nullable=False, default=datetime.date.today)
    complaint = Column(Text, default="")
    diagnosis = Column(Text, default="")
    prescription = Column(Text, default="")
    notes = Column(Text, default="")

    patient = relationship("Patient", back_populates="medical_records")
