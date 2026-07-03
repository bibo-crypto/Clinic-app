"""Invoice / Billing model."""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
import datetime


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    invoice_date = Column(Date, nullable=False, default=datetime.date.today)
    consultation_fee = Column(Float, default=0.0)
    additional_services = Column(Text, default="[]")  # JSON list of {name, price}
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)
    notes = Column(String(300), default="")

    patient = relationship("Patient", back_populates="invoices")
