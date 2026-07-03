"""Doctor CRUD controller."""

from database.db import get_session
from models.doctor import Doctor


def get_all():
    session = get_session()
    try:
        return session.query(Doctor).order_by(Doctor.full_name).all()
    finally:
        session.close()


def get_by_id(doctor_id: int):
    session = get_session()
    try:
        return session.query(Doctor).filter_by(id=doctor_id).first()
    finally:
        session.close()


def add(data: dict) -> Doctor:
    session = get_session()
    try:
        doctor = Doctor(**data)
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        session.expunge(doctor)
        return doctor
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update(doctor_id: int, data: dict) -> bool:
    session = get_session()
    try:
        doctor = session.query(Doctor).filter_by(id=doctor_id).first()
        if not doctor:
            return False
        for key, value in data.items():
            setattr(doctor, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete(doctor_id: int) -> bool:
    session = get_session()
    try:
        doctor = session.query(Doctor).filter_by(id=doctor_id).first()
        if not doctor:
            return False
        session.delete(doctor)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
