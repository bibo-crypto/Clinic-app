"""
Clinic Management System — Entry Point
Run:  python main.py
"""

import sys
import os

# Make sure imports resolve from the clinic-app root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database.db import init_db
from controllers import settings_controller
from utils import language as lang
from utils import theme


def start_login():
    """Show the login window. Called on startup and after logout."""
    from views.login_view import LoginView

    root = ctk.CTk()
    root.title(lang.t("app_title"))
    root.geometry("900x620")
    root.resizable(False, False)
    root.configure(fg_color=theme.get("content_bg"))

    def on_success(user):
        root.destroy()
        start_main(user)

    login_view = LoginView(root, on_success)
    login_view.pack(fill="both", expand=True)
    root.mainloop()


def start_main(user):
    """Show the main application window after successful login."""
    from views.main_window import MainWindow
    app = MainWindow(user)
    app.mainloop()


def main():
    # Initialise database (creates tables + seeds defaults)
    init_db()

    # Load settings
    settings = settings_controller.get()
    theme_name = settings.theme if settings else "light"
    language_code = settings.language if settings else "en"

    # Apply theme and language
    theme.apply(theme_name)
    lang.load(language_code)

    start_login()


if __name__ == "__main__":
    main()
