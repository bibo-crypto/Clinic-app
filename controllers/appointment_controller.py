"""Appointment CRUD controller with double-booking prevention."""

import datetime
from database.db import get_session
from models.appointment import Appointment


def get_all():
    session = get_session()
    try:
        return (
            session.query(Appointment)
            .order_by(Appointment.date.desc(), Appointment.time.asc())
            .all()
        )
    finally:
        session.close()


def get_today():
    session = get_session()
    try:
        today = datetime.date.today()
        return (
            session.query(Appointment)
            .filter(Appointment.date == today)
            .order_by(Appointment.time.asc())
            .all()
        )
    finally:
        session.close()


def count_today() -> int:
    session = get_session()
    try:
        return session.query(Appointment).filter(Appointment.date == datetime.date.today()).count()
    finally:
        session.close()


def check_double_booking(doctor_id: int, date, time, exclude_id: int = None) -> bool:
    """Return True if doctor already has an appointment at that date/time."""
    session = get_session()
    try:
        q = session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.time == time,
            Appointment.status != "cancelled",
        )
        if exclude_id:
            q = q.filter(Appointment.id != exclude_id)
        return q.first() is not None
    finally:
        session.close()


def add(data: dict) -> Appointment:
    session = get_session()
    try:
        appt = Appointment(**data)
        session.add(appt)
        session.commit()
        session.refresh(appt)
        session.expunge(appt)
        return appt
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update(appt_id: int, data: dict) -> bool:
    session = get_session()
    try:
        appt = session.query(Appointment).filter_by(id=appt_id).first()
        if not appt:
            return False
        for key, value in data.items():
            setattr(appt, key, value)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete(appt_id: int) -> bool:
    session = get_session()
    try:
        appt = session.query(Appointment).filter_by(id=appt_id).first()
        if not appt:
            return False
        session.delete(appt)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
