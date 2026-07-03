"""Reports view — generate PDF and Excel reports."""

import datetime
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import report_controller, patient_controller


class ReportsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=lang.t("reports"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(anchor="w", padx=28, pady=(24, 16))

        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        row_frame.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # Daily report card
        self._report_card(
            row_frame, 0,
            lang.t("daily_report"),
            "📅",
            "#1976d2",
            self._build_daily_controls,
        )
        # Monthly report card
        self._report_card(
            row_frame, 1,
            lang.t("monthly_report"),
            "📊",
            "#388e3c",
            self._build_monthly_controls,
        )
        # Patient report card
        self._report_card(
            row_frame, 2,
            lang.t("patient_report"),
            "👤",
            "#7b1fa2",
            self._build_patient_controls,
        )

    def _report_card(self, parent, col, title, icon, color, controls_fn):
        card = ctk.CTkFrame(parent, fg_color=theme.get("card_bg"), corner_radius=12)
        card.grid(row=0, column=col, padx=8, sticky="nsew", pady=0)

        ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=40)).pack(pady=(24, 4))
        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=color).pack(pady=(0, 12))

        controls_fn(card, color)

    def _build_daily_controls(self, card, color):
        today = datetime.date.today()
        ctk.CTkLabel(card, text=lang.t("appointment_date") + " (YYYY-MM-DD)",
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).pack(padx=20)
        self.daily_date_e = ctk.CTkEntry(card, fg_color=theme.get("entry_bg"),
                                         text_color=theme.get("entry_fg"),
                                         border_color=theme.get("border"))
        self.daily_date_e.insert(0, str(today))
        self.daily_date_e.pack(padx=20, pady=4, fill="x")

        ctk.CTkButton(card, text=lang.t("export_pdf"),
                      fg_color=color, corner_radius=8,
                      command=self._daily_pdf).pack(padx=20, pady=4, fill="x")
        ctk.CTkButton(card, text=lang.t("export_excel"),
                      fg_color=color, corner_radius=8,
                      command=self._daily_excel).pack(padx=20, pady=(0, 24), fill="x")

    def _build_monthly_controls(self, card, color):
        today = datetime.date.today()
        ctk.CTkLabel(card, text="Year",
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).pack(padx=20)
        self.month_year_e = ctk.CTkEntry(card, fg_color=theme.get("entry_bg"),
                                         text_color=theme.get("entry_fg"),
                                         border_color=theme.get("border"))
        self.month_year_e.insert(0, str(today.year))
        self.month_year_e.pack(padx=20, pady=4, fill="x")

        ctk.CTkLabel(card, text="Month (1-12)",
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).pack(padx=20)
        self.month_e = ctk.CTkEntry(card, fg_color=theme.get("entry_bg"),
                                    text_color=theme.get("entry_fg"),
                                    border_color=theme.get("border"))
        self.month_e.insert(0, str(today.month))
        self.month_e.pack(padx=20, pady=4, fill="x")

        ctk.CTkButton(card, text=lang.t("export_pdf"),
                      fg_color=color, corner_radius=8,
                      command=self._monthly_pdf).pack(padx=20, pady=4, fill="x")
        ctk.CTkButton(card, text=lang.t("export_excel"),
                      fg_color=color, corner_radius=8,
                      command=self._monthly_excel).pack(padx=20, pady=(0, 24), fill="x")

    def _build_patient_controls(self, card, color):
        patients = patient_controller.get_all()
        names = [f"{p.id} — {p.full_name}" for p in patients]
        self._patients = patients
        ctk.CTkLabel(card, text=lang.t("select_patient"),
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).pack(padx=20)
        self.patient_menu = ctk.CTkOptionMenu(card, values=names or ["—"])
        self.patient_menu.pack(padx=20, pady=4, fill="x")

        ctk.CTkButton(card, text=lang.t("export_pdf"),
                      fg_color=color, corner_radius=8,
                      command=self._patient_pdf).pack(padx=20, pady=(8, 24), fill="x")

    # ── Actions ────────────────────────────────────────────────────────────────

    def _open_file(self, path):
        try:
            if sys.platform == "win32":
                subprocess.Popen(["start", path], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass
        messagebox.showinfo(lang.t("success"), f"Saved to:\n{path}")

    def _daily_pdf(self):
        try:
            d = datetime.date.fromisoformat(self.daily_date_e.get().strip())
            path = report_controller.daily_report_pdf(d)
            self._open_file(path)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))

    def _daily_excel(self):
        try:
            d = datetime.date.fromisoformat(self.daily_date_e.get().strip())
            path = report_controller.daily_report_excel(d)
            self._open_file(path)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))

    def _monthly_pdf(self):
        try:
            y = int(self.month_year_e.get().strip())
            m = int(self.month_e.get().strip())
            path = report_controller.monthly_report_pdf(y, m)
            self._open_file(path)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))

    def _monthly_excel(self):
        try:
            y = int(self.month_year_e.get().strip())
            m = int(self.month_e.get().strip())
            path = report_controller.monthly_report_excel(y, m)
            self._open_file(path)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))

    def _patient_pdf(self):
        try:
            val = self.patient_menu.get()
            pid = int(val.split("—")[0].strip())
            path = report_controller.patient_report_pdf(pid)
            self._open_file(path)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))
