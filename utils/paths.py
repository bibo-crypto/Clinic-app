import os
import sys
from pathlib import Path
from typing import Optional


def get_app_root(module_file: Optional[str] = None, frozen: Optional[bool] = None, executable_path: Optional[str] = None) -> Path:
    """Return the application root directory for source and frozen runs."""
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))

    if frozen:
        for candidate in [executable_path, getattr(sys, "executable", None)]:
            if candidate:
                exe = Path(candidate).expanduser()
                if exe.is_file():
                    return exe.parent
        return Path.cwd()

    if module_file:
        module_path = Path(module_file).expanduser().resolve()
        if module_path.is_file():
            return module_path.parent.parent
    return Path(__file__).resolve().parent.parent


def get_runtime_data_dir(module_file: Optional[str] = None, frozen: Optional[bool] = None, executable_path: Optional[str] = None) -> Path:
    """Return a stable directory for runtime data such as the database and reports."""
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))

    if frozen:
        local_appdata = os.environ.get("LOCALAPPDATA") or os.path.join(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")), "..", "Local")
        return Path(local_appdata).expanduser() / "ClinicSystem"

    return get_app_root(module_file=module_file, frozen=False, executable_path=executable_path)


def get_resource_path(*parts: str) -> Path:
    """Resolve a bundled resource path for source and frozen execution."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS).resolve()
    else:
        base = Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)
