"""Main application window with sidebar navigation."""

import customtkinter as ctk
from utils import language as lang
from utils import theme


class MainWindow(ctk.CTk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(lang.t("app_title"))
        self.geometry("1280x760")
        self.minsize(1024, 640)
        self._active_btn = None
        self._build()
        self._navigate("dashboard")

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0,
                               fg_color=theme.get("sidebar_bg"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(20, weight=1)  # push logout to bottom

        # Logo / title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=80)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 8))
        ctk.CTkLabel(logo_frame, text="🏥",
                     font=ctk.CTkFont(size=32)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(logo_frame, text="Clinic\nSystem",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.get("sidebar_text"),
                     justify="left").pack(side="left")

        # User info
        ctk.CTkLabel(sidebar, text=f"{lang.t('welcome')}, {self.user.full_name.split()[0]}",
                     font=ctk.CTkFont(size=11),
                     text_color="#aaaacc").grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))

        # Separator
        ctk.CTkFrame(sidebar, height=1, fg_color="#2a2a5a").grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))

        # Nav items: (key, icon, label)
        nav_items = [
            ("dashboard", "📊", lang.t("dashboard")),
            ("patients", "👥", lang.t("patients")),
            ("doctors", "👨‍⚕️", lang.t("doctors")),
            ("appointments", "📅", lang.t("appointments")),
            ("medical_records", "📋", lang.t("medical_records")),
            ("billing", "💳", lang.t("billing")),
            ("reports", "📈", lang.t("reports")),
            ("settings", "⚙️", lang.t("settings")),
        ]

        self._nav_buttons = {}
        for i, (key, icon, label) in enumerate(nav_items, 3):
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=theme.get("sidebar_text"),
                hover_color=theme.get("sidebar_hover"),
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._navigate(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=2, sticky="ew")
            self._nav_buttons[key] = btn

        # Logout
        ctk.CTkButton(
            sidebar,
            text="  🚪  " + lang.t("logout"),
            anchor="w",
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="#ff8a80",
            hover_color=theme.get("sidebar_hover"),
            font=ctk.CTkFont(size=13),
            command=self._logout,
        ).grid(row=21, column=0, padx=12, pady=(8, 20), sticky="ew")

        # ── Content area ──────────────────────────────────────────────────────
        self.content = ctk.CTkFrame(self, corner_radius=0,
                                    fg_color=theme.get("content_bg"))
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current_view = None

    def _navigate(self, key: str):
        # Highlight active
        if self._active_btn:
            self._active_btn.configure(fg_color="transparent")
        btn = self._nav_buttons.get(key)
        if btn:
            btn.configure(fg_color=theme.get("sidebar_active"))
            self._active_btn = btn

        # Destroy old view
        if self._current_view:
            self._current_view.destroy()

        # Lazy-import to avoid circular dependencies
        view = self._create_view(key)
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

    def _create_view(self, key: str):
        if key == "dashboard":
            from views.dashboard_view import DashboardView
            return DashboardView(self.content)
        elif key == "patients":
            from views.patients_view import PatientsView
            return PatientsView(self.content)
        elif key == "doctors":
            from views.doctors_view import DoctorsView
            return DoctorsView(self.content)
        elif key == "appointments":
            from views.appointments_view import AppointmentsView
            return AppointmentsView(self.content)
        elif key == "medical_records":
            from views.medical_records_view import MedicalRecordsView
            return MedicalRecordsView(self.content)
        elif key == "billing":
            from views.billing_view import BillingView
            return BillingView(self.content)
        elif key == "reports":
            from views.reports_view import ReportsView
            return ReportsView(self.content)
        elif key == "settings":
            from views.settings_view import SettingsView
            return SettingsView(self.content, self.user)
        # Fallback
        return ctk.CTkFrame(self.content, fg_color="transparent")

    def _logout(self):
        self.destroy()
        # Re-launch login
        import main
        main.start_login()
