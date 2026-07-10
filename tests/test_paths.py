import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.first_run import generate_admin_password, generate_setup_credentials
from utils.paths import get_app_root, get_runtime_data_dir


class TestRuntimePaths(unittest.TestCase):
    def test_frozen_mode_uses_local_appdata_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["LOCALAPPDATA"] = tmp
            data_dir = get_runtime_data_dir(module_file=__file__, frozen=True)
            self.assertEqual(data_dir, Path(tmp) / "ClinicSystem")

    def test_source_mode_uses_project_root_for_data(self):
        root = Path(__file__).resolve().parent.parent
        data_dir = get_runtime_data_dir(module_file=__file__, frozen=False)
        self.assertEqual(data_dir, root)

    def test_app_root_uses_executable_directory_when_frozen(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "ClinicSystem.exe"
            exe.touch()
            app_root = get_app_root(module_file=__file__, frozen=True, executable_path=str(exe))
            self.assertEqual(app_root, Path(tmp))

    def test_generate_admin_password_writes_file_on_desktop(self):
        with tempfile.TemporaryDirectory() as tmp:
            desktop_dir = Path(tmp)
            with patch("database.first_run._desktop_dir", return_value=desktop_dir):
                password_file = desktop_dir / "ClinicSystem_ADMIN_PASSWORD.txt"
                if password_file.exists():
                    password_file.unlink()

                generated_password = generate_admin_password()

                self.assertTrue(password_file.exists())
                self.assertIn(generated_password, password_file.read_text(encoding="utf-8"))

    def test_generate_setup_credentials_creates_password_and_reset_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            desktop_dir = Path(tmp)
            with patch("database.first_run._desktop_dir", return_value=desktop_dir):
                credentials = generate_setup_credentials("admin")

            self.assertTrue(credentials["password_file"].exists())
            self.assertTrue(credentials["reset_password_file"].exists())
            self.assertIn(credentials["password"], credentials["password_file"].read_text(encoding="utf-8"))
            self.assertIn(credentials["reset_password"], credentials["reset_password_file"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
