import os
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
