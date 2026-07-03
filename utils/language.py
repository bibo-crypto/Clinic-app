"""Language manager — loads en.json or ar.json and provides translation."""

import json
import os

_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "languages")
_strings: dict = {}
_current_lang: str = "en"


def load(lang: str = "en") -> None:
    """Load a language file (\"en\" or \"ar\")."""
    global _strings, _current_lang
    path = os.path.join(_BASE, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(_BASE, "en.json")
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
