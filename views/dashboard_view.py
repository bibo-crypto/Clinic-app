"""Dashboard view — summary cards and today's appointments."""

import customtkinter as ctk
import datetime
from utils import language as lang
from utils import theme
from controllers import patient_controller, appointment_controller, billing_controller


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build()

    def _build(self):
        # Title
        ctk.CTkLabel(self, text=lang.t("dashboard"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(self, text=str(datetime.date.today()),
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=28, pady=(0, 16))

        # Stats cards row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=28, pady=(0, 20))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        cards = [
            (lang.t("today_appointments"), str(appointment_controller.count_today()), "#1976d2", "📅"),
            (lang.t("total_patients"), str(patient_controller.count()), "#388e3c", "👥"),
            (lang.t("today_revenue"), f"${billing_controller.today_revenue():.2f}", "#f57c00", "💰"),
            (lang.t("monthly_revenue"), f"${billing_controller.monthly_revenue():.2f}", "#7b1fa2", "📊"),
        ]
        for col, (title, value, color, icon) in enumerate(cards):
            card = ctk.CTkFrame(stats_frame, fg_color=theme.get("card_bg"),
                                corner_radius=12)
            card.grid(row=0, column=col, padx=6, pady=0, sticky="ew")
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(16, 4))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=26, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=title, text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=12)).pack(pady=(2, 16))

        # Today's appointments table
        ctk.CTkLabel(self, text=lang.t("today_appointments"),
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=theme.get("text_primary")).pack(anchor="w", padx=28, pady=(0, 8))

        table_card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        table_card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        # Header row
        header = ctk.CTkFrame(table_card, fg_color=theme.get("table_header"), corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        cols = ["#", lang.t("patient"), lang.t("doctor"), lang.t("appointment_time"), lang.t("status")]
        widths = [40, 200, 200, 120, 120]
        for i, (c, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(header, text=c, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=theme.get("text_primary")).grid(row=0, column=i, padx=8, pady=8, sticky="w")

        # Scrollable rows
        scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        appointments = appointment_controller.get_today()
        if not appointments:
            ctk.CTkLabel(scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
        else:
            status_colors = {
                "scheduled": theme.get("accent"),
                "completed": theme.get("success"),
                "cancelled": theme.get("danger"),
            }
            for idx, appt in enumerate(appointments):
                bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
                row_frame = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=0, height=38)
                row_frame.pack(fill="x")
                row_frame.pack_propagate(False)
                cells = [
                    str(idx + 1),
                    appt.patient.full_name if appt.patient else "",
                    appt.doctor.full_name if appt.doctor else "",
                    str(appt.time)[:5],
                    appt.status,
                ]
                for ci, (val, w) in enumerate(zip(cells, widths)):
                    color = status_colors.get(val, theme.get("text_primary")) if ci == 4 else theme.get("text_primary")
                    ctk.CTkLabel(row_frame, text=val, width=w,
                                 text_color=color,
                                 font=ctk.CTkFont(size=12)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
