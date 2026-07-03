"""Medical records controller."""

from database.db import get_session
from models.medical_record import MedicalRecord


def get_by_patient(patient_id: int):
    session = get_session()
    try:
        return (
            session.query(MedicalRecord)
            .filter_by(patient_id=patient_id)
            .order_by(MedicalRecord.visit_date.desc())
            .all()
        )
    finally:
        session.close()


def add(data: dict) -> MedicalRecord:
    session = get_session()
    try:
        record = MedicalRecord(**data)
        session.add(record)
        session.commit()
        session.refresh(record)
        session.expunge(record)
        return record
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update(record_id: int, data: dict) -> bool:
    session = get_session()
    try:
        record = session.query(MedicalRecord).filter_by(id=record_id).first()
        if not record:
            return False
        for key, value in data.items():
            setattr(record, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete(record_id: int) -> bool:
    session = get_session()
    try:
        record = session.query(MedicalRecord).filter_by(id=record_id).first()
        if not record:
            return False
        session.delete(record)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
