# Clinic Management System

A professional desktop application for managing clinic operations — patients, doctors, appointments, medical records, billing, and reports. Built with Python 3.13 and CustomTkinter.

---

## Features

- **Login system** with roles: Administrator, Doctor, Receptionist
- **Dashboard** — today's appointments, patient count, revenue stats
- **Patients** — full CRUD with search, medical notes, blood type, allergies
- **Doctors** — manage specializations and consultation fees
- **Appointments** — scheduling with double-booking prevention
- **Medical Records** — per-patient visit history (complaint, diagnosis, prescription)
- **Billing** — invoices with additional services, discounts, and paid/unpaid tracking
- **Reports** — daily, monthly, and patient reports exported to PDF and Excel
- **Settings** — clinic name, logo, light/dark theme, English/Arabic language toggle
- **Bilingual** — full English and Arabic (RTL) support via language files

---

## Project Structure

```
clinic-app/
├── main.py               # Entry point
├── requirements.txt
├── assets/               # Icons and images
├── backups/              # DB backups (future use)
├── database/
│   └── db.py             # SQLAlchemy engine + session + init
├── exports/              # Generated PDF and Excel files
├── languages/
│   ├── en.json           # English strings
│   └── ar.json           # Arabic strings
├── models/               # SQLAlchemy ORM models
│   ├── user.py
│   ├── patient.py
│   ├── doctor.py
│   ├── appointment.py
│   ├── medical_record.py
│   ├── invoice.py
│   └── setting.py
├── controllers/          # Business logic (no UI)
│   ├── auth_controller.py
│   ├── patient_controller.py
│   ├── doctor_controller.py
│   ├── appointment_controller.py
│   ├── medical_record_controller.py
│   ├── billing_controller.py
│   ├── report_controller.py
│   └── settings_controller.py
├── views/                # CustomTkinter UI screens
│   ├── login_view.py
│   ├── main_window.py
│   ├── dashboard_view.py
│   ├── patients_view.py
│   ├── doctors_view.py
│   ├── appointments_view.py
│   ├── medical_records_view.py
│   ├── billing_view.py
│   ├── reports_view.py
│   └── settings_view.py
└── utils/
    ├── language.py       # Translation helper (t("key"))
    └── theme.py          # Theme color registry
```

---

## How to Run

### 1. Install Python 3.13+

Download from https://python.org and make sure `python` is in your PATH.

### 2. Install dependencies

```bash
cd clinic-app
pip install -r requirements.txt
```

### 3. Run the application

```bash
python main.py
```

The SQLite database is created automatically at `database/clinic.db` on first run.

---

## Default Login

| Username | Password  | Role          |
|----------|-----------|---------------|
| admin    | admin123  | Administrator |

---

## Switching Language

Go to **Settings → Language** and select English or Arabic. Restart the app for the change to take full effect.

## Switching Theme

Go to **Settings → Theme** and choose Light or Dark. Takes effect on the next restart.

---

## Exported Files

- **PDF reports** → `exports/` directory
- **Excel reports** → `exports/` directory

---

## Requirements

- Python 3.13+
- customtkinter
- SQLAlchemy
- Pillow
- openpyxl
- reportlab
- bcrypt
