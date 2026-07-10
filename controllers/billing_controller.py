"""Billing / Invoice controller."""

import json
import datetime
from database.db import get_session
from models.invoice import Invoice


def get_all():
    session = get_session()
    try:
        from sqlalchemy.orm import joinedload
        invoices = (
            session.query(Invoice)
            .options(joinedload(Invoice.patient))
            .order_by(Invoice.invoice_date.desc())
            .all()
        )
        # Serialize to dicts to avoid lazy-loading issues after session close
        result = []
        for inv in invoices:
            try:
                result.append({
                    'id': inv.id,
                    'patient_id': inv.patient_id,
                    'patient_name': inv.patient.full_name if inv.patient else 'Unknown',
                    'doctor_id': inv.doctor_id,
                    'doctor_name': inv.doctor.full_name if inv.doctor else '',
                    'invoice_date': inv.invoice_date,
                    'consultation_fee': inv.consultation_fee,
                    'additional_services': inv.additional_services,
                    'discount': inv.discount,
                    'total_amount': inv.total_amount,
                    'is_paid': inv.is_paid,
                    'notes': inv.notes,
                })
            except Exception as item_err:
                print(f"Error serializing invoice {inv.id}: {item_err}")
                continue
        print(f"get_all() returned {len(result)} invoices")
        return result
    except Exception as e:
        print(f"Error in get_all: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        session.close()


def get_by_patient(patient_id: int):
    session = get_session()
    try:
        from sqlalchemy.orm import joinedload
        invoices = (
            session.query(Invoice)
            .options(joinedload(Invoice.patient))
            .filter_by(patient_id=patient_id)
            .order_by(Invoice.invoice_date.desc())
            .all()
        )
        # Serialize to dicts to avoid lazy-loading issues after session close
        result = []
        for inv in invoices:
            result.append({
                'id': inv.id,
                'patient_id': inv.patient_id,
                'patient_name': inv.patient.full_name if inv.patient else '',
                'doctor_id': inv.doctor_id,
                'doctor_name': inv.doctor.full_name if inv.doctor else '',
                'invoice_date': inv.invoice_date,
                'consultation_fee': inv.consultation_fee,
                'additional_services': inv.additional_services,
                'discount': inv.discount,
                'total_amount': inv.total_amount,
                'is_paid': inv.is_paid,
                'notes': inv.notes,
            })
        return result
    except Exception as e:
        print(f"Error in get_by_patient: {e}")
        return []
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
        print(f"Creating invoice with data: {data}")
        invoice = Invoice(**data)
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        inv_id = invoice.id
        print(f"Invoice created with ID: {inv_id}")
        session.expunge_all()
        return invoice
    except Exception as e:
        session.rollback()
        print(f"Error adding invoice: {e}")
        import traceback
        traceback.print_exc()
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
