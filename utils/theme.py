"""Theme configuration for CustomTkinter."""

import customtkinter as ctk

THEMES = {
    "light": {
        "appearance": "light",
        "color_theme": "blue",
        "sidebar_bg": "#1a237e",
        "sidebar_hover": "#283593",
        "sidebar_text": "#ffffff",
        "sidebar_active": "#3949ab",
        "content_bg": "#f5f5f5",
        "card_bg": "#ffffff",
        "text_primary": "#1a1a2e",
        "text_secondary": "#666666",
        "accent": "#1976d2",
        "accent_hover": "#1565c0",
        "danger": "#d32f2f",
        "success": "#388e3c",
        "warning": "#f57c00",
        "border": "#e0e0e0",
        "table_header": "#e3f2fd",
        "table_row_alt": "#f9f9f9",
        "entry_bg": "#ffffff",
        "entry_fg": "#1a1a2e",
    },
    "dark": {
        "appearance": "dark",
        "color_theme": "blue",
        "sidebar_bg": "#0d0d1a",
        "sidebar_hover": "#1a1a2e",
        "sidebar_text": "#e0e0e0",
        "sidebar_active": "#1976d2",
        "content_bg": "#1e1e2e",
        "card_bg": "#2a2a3e",
        "text_primary": "#e0e0e0",
        "text_secondary": "#9e9e9e",
        "accent": "#42a5f5",
        "accent_hover": "#1976d2",
        "danger": "#ef5350",
        "success": "#66bb6a",
        "warning": "#ffa726",
        "border": "#3a3a4e",
        "table_header": "#252535",
        "table_row_alt": "#252535",
        "entry_bg": "#2a2a3e",
        "entry_fg": "#e0e0e0",
    },
}

_current: dict = THEMES["light"]


def apply(theme_name: str) -> None:
    """Apply a named theme (\"light\" or \"dark\")."""
    global _current
    _current = THEMES.get(theme_name, THEMES["light"])
    ctk.set_appearance_mode(_current["appearance"])
    ctk.set_default_color_theme(_current["color_theme"])


def get(key: str, fallback: str = "#ffffff") -> str:
    """Get a color value from the active theme."""
    return _current.get(key, fallback)
