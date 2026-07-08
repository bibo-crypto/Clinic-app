"""Language manager — loads en.json or ar.json and provides translation."""

import json
import os
from pathlib import Path

from utils.paths import get_resource_path

_BASE = get_resource_path("languages")
_strings: dict = {}
_current_lang: str = "en"


def load(lang: str = "en") -> None:
    """Load a language file (\"en\" or \"ar\")."""
    global _strings, _current_lang
    path = _BASE / f"{lang}.json"
    if not path.exists():
        path = _BASE / "en.json"
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)
    _current_lang = lang


def t(key: str) -> str:
    """Return the translated string for *key*, falling back to the key itself."""
    return _strings.get(key, key)


def current() -> str:
    """Return the active language code."""
    return _current_lang


def is_rtl() -> bool:
    """Return True if the current language is RTL (Arabic)."""
    return _current_lang == "ar"
