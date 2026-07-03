"""
database/first_run.py
─────────────────────
يولّد كلمة مرور عشوائية آمنة للمسؤول عند أول تشغيل،
ويكتبها في ملف نصي على سطح المكتب.
"""

import os
import secrets
from pathlib import Path


def _desktop_dir() -> Path:
    """يحدد مسار سطح المكتب بشكل موثوق (يدعم OneDrive على ويندوز)."""
    # محاولة مسار OneDrive أولاً (شائع على Windows 10/11)
    onedrive = os.environ.get("OneDriveConsumer") or os.environ.get("OneDrive")
    if onedrive:
        p = Path(onedrive) / "Desktop"
        if p.is_dir():
            return p

    # سطح المكتب العادي
    p = Path.home() / "Desktop"
    if p.is_dir():
        return p

    # fallback: المجلد الحالي
    return Path.cwd()


def generate_admin_password() -> str:
    """يولّد كلمة مرور عشوائية آمنة ويكتبها على سطح المكتب."""
    password = secrets.token_urlsafe(10)  # ~13 حرف عشوائي

    try:
        desktop = _desktop_dir()
        file_path = desktop / "ClinicSystem_ADMIN_PASSWORD.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Clinic Management System — كلمة مرور المسؤول الأولى\n")
            f.write("=" * 50 + "\n")
            f.write(f"Username : admin\n")
            f.write(f"Password : {password}\n")
            f.write("=" * 50 + "\n")
            f.write("⚠️  احذف هذا الملف بعد أول تسجيل دخول.\n")
            f.write("    يمكنك تغيير كلمة المرور لاحقاً من شاشة الإعدادات.\n")
            f.write("\n")
            f.write("لو نسيت كلمة المرور:\n")
            f.write("  احذف ملف database/clinic.db وشغّل البرنامج من جديد.\n")
    except Exception:
        pass  # عدم القدرة على الكتابة لسطح المكتب لا يوقف البرنامج

    return password
