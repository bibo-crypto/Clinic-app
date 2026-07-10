"""
database/first_run.py
─────────────────────
يولّد كلمة مرور عشوائية آمنة للمسؤول عند أول تشغيل،
ويكتبها في ملف نصي على سطح المكتب.
"""

import os
import secrets
from pathlib import Path


RESET_TOKEN_LENGTH = 10


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


def get_password_file_path() -> Path:
    """Return the path for the password text file on the desktop."""
    return _desktop_dir() / "ClinicSystem_ADMIN_PASSWORD.txt"


def _read_file_value(file_path: Path, prefix: str) -> str | None:
    """Read a value from a text file if present."""
    if not file_path.exists():
        return None
    for line in file_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def write_password_file(username: str, password: str, reset_token: str | None = None) -> Path:
    """Write the provided credentials to a text file on the desktop."""
    file_path = get_password_file_path()
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Clinic Management System — Password File\n")
            f.write("=" * 50 + "\n")
            f.write(f"Username : {username}\n")
            f.write(f"Password : {password}\n")
            if reset_token:
                f.write(f"Reset Token : {reset_token}\n")
            f.write("=" * 50 + "\n")
            f.write("This file is created on the desktop for setup and recovery.\n")
            f.write("You can reset the password from the login screen if needed.\n")
    except Exception:
        pass

    return file_path


def write_reset_password_file(reset_token: str) -> Path:
    """Create a desktop file containing the reset token for setup and recovery."""
    file_path = _desktop_dir() / "ClinicSystem_RESET_PASSWORD.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Clinic Management System — Reset Password File\n")
            f.write("=" * 50 + "\n")
            f.write(f"Reset Password : {reset_token}\n")
            f.write("=" * 50 + "\n")
            f.write("Use this token when changing the admin password from the login screen.\n")
    except Exception:
        pass

    return file_path


def ensure_setup_credentials(username: str = "admin") -> dict[str, str | Path]:
    """Ensure the password and reset-token files exist for setup or recovery."""
    password_file = get_password_file_path()
    reset_password_file = password_file.with_name("ClinicSystem_RESET_PASSWORD.txt")

    existing_password = _read_file_value(password_file, "Password")
    existing_reset = _read_file_value(reset_password_file, "Reset Password")

    if password_file.exists() and reset_password_file.exists() and existing_password and existing_reset:
        return {
            "username": username,
            "password": existing_password,
            "reset_password": existing_reset,
            "password_file": password_file,
            "reset_password_file": reset_password_file,
        }

    password = existing_password or secrets.token_urlsafe(10)
    reset_token = existing_reset or secrets.token_urlsafe(RESET_TOKEN_LENGTH)
    password_file = write_password_file(username, password, reset_token)
    reset_password_file = write_reset_password_file(reset_token)
    return {
        "username": username,
        "password": password,
        "reset_password": reset_token,
        "password_file": password_file,
        "reset_password_file": reset_password_file,
    }


def generate_setup_credentials(username: str = "admin") -> dict[str, str | Path]:
    """Create password and reset-token files for the first setup."""
    return ensure_setup_credentials(username)


def generate_admin_password() -> str:
    """Generate a random admin password and write it to the password file."""
    credentials = generate_setup_credentials("admin")
    return str(credentials["password"])
