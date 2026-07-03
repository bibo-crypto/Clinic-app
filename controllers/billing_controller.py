"""Billing / Invoice controller."""

import json
import datetime
from database.db import get_session
from models.invoice import Invoice


def get_all():
    session = get_session()
    try:
        return (
            session.query(Invoice)
            .order_by(Invoice.invoice_date.desc())
            .all()
        )
    finally:
        session.close()


def get_by_patient(patient_id: int):
    session = get_session()
    try:
        return (
            session.query(Invoice)
            .filter_by(patient_id=patient_id)
            .order_by(Invoice.invoice_date.desc())
            .all()
        )
    finally:
        session.close()


def today_revenue() -> float:
    session = get_session()
    try:
        today = datetime.date.today()
        invoices = session.query(Invoice).filter(Invoice.invoice_date == today).all()
        return sum(inv.total_amount for inv in invoices)
    finally:
        session.close()


def monthly_revenue(year: int = None, month: int = None) -> float:
    session = get_session()
    try:
        today = datetime.date.today()
        year = year or today.year
        month = month or today.month
        invoices = session.query(Invoice).filter(
            Invoice.invoice_date >= datetime.date(year, month, 1)
        ).all()
        return sum(
            inv.total_amount
            for inv in invoices
            if inv.invoice_date.month == month and inv.invoice_date.year == year
        )
    finally:
        session.close()


def add(data: dict) -> Invoice:
    session = get_session()
    try:
        if "additional_services" in data and isinstance(data["additional_services"], list):
            data["additional_services"] = json.dumps(data["additional_services"])
        invoice = Invoice(**data)
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        session.expunge(invoice)
        return invoice
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update(invoice_id: int, data: dict) -> bool:
    session = get_session()
    try:
        inv = session.query(Invoice).filter_by(id=invoice_id).first()
        if not inv:
            return False
        if "additional_services" in data and isinstance(data["additional_services"], list):
            data["additional_services"] = json.dumps(data["additional_services"])
        for key, value in data.items():
            setattr(inv, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def mark_paid(invoice_id: int) -> bool:
    return update(invoice_id, {"is_paid": True})


def delete(invoice_id: int) -> bool:
    session = get_session()
    try:
        inv = session.query(Invoice).filter_by(id=invoice_id).first()
        if not inv:
            return False
        session.delete(inv)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
