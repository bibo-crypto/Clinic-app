"""Patient CRUD controller."""

from database.db import get_session
from models.patient import Patient


def get_all():
    session = get_session()
    try:
        return session.query(Patient).order_by(Patient.full_name).all()
    finally:
        session.close()


def search(query: str):
    session = get_session()
    try:
        q = f"%{query}%"
        return (
            session.query(Patient)
            .filter(Patient.full_name.ilike(q) | Patient.phone.ilike(q))
            .all()
        )
    finally:
        session.close()


def get_by_id(patient_id: int):
    session = get_session()
    try:
        return session.query(Patient).filter_by(id=patient_id).first()
    finally:
        session.close()


def add(data: dict) -> Patient:
    session = get_session()
    try:
        patient = Patient(**data)
        session.add(patient)
        session.commit()
        session.refresh(patient)
        session.expunge(patient)
        return patient
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update(patient_id: int, data: dict) -> bool:
    session = get_session()
    try:
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if not patient:
            return False
        for key, value in data.items():
            setattr(patient, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete(patient_id: int) -> bool:
    session = get_session()
    try:
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if not patient:
            return False
        session.delete(patient)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def count() -> int:
    session = get_session()
    try:
        return session.query(Patient).count()
    finally:
        session.close()
