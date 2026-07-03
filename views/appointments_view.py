"""Appointments management view."""

import datetime
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import appointment_controller, patient_controller, doctor_controller

STATUSES = ["scheduled", "completed", "cancelled"]


class AppointmentsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("appointments"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

        for label, cmd, color in [
            (lang.t("add"), self._open_add, theme.get("accent")),
            (lang.t("edit"), self._open_edit, theme.get("warning")),
            (lang.t("delete"), self._delete, theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=90, fg_color=color,
                          hover_color=theme.get("accent_hover"),
                          corner_radius=8, command=cmd).pack(side="right", padx=4)

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        headers = ["ID", lang.t("patient"), lang.t("doctor"),
                   lang.t("appointment_date"), lang.t("appointment_time"), lang.t("status")]
        widths = [50, 180, 180, 110, 80, 100]

        hf = ctk.CTkFrame(card, fg_color=theme.get("table_header"), corner_radius=0)
        hf.pack(fill="x")
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=theme.get("text_primary")).grid(row=0, column=i, padx=8, pady=8, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self._widths = widths

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        appts = appointment_controller.get_all()
        if not appts:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        status_colors = {
            "scheduled": theme.get("accent"),
            "completed": theme.get("success"),
            "cancelled": theme.get("danger"),
        }
        for idx, a in enumerate(appts):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            vals = [
                str(a.id),
                a.patient.full_name if a.patient else "",
                a.doctor.full_name if a.doctor else "",
                str(a.date),
                str(a.time)[:5],
                lang.t(f"status_{a.status}"),
            ]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                color = status_colors.get(a.status, theme.get("text_primary")) if ci == 5 else theme.get("text_primary")
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=color,
                             font=ctk.CTkFont(size=12)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            aid = a.id
            row.bind("<Button-1>", lambda e, i=aid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=aid: self._select(i))

    def _select(self, aid):
        self._selected_id = aid

    def _open_add(self):
        AppointmentFormDialog(self, None, self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("edit"), "Please select an appointment first.")
            return
        appts = appointment_controller.get_all()
        appt = next((a for a in appts if a.id == self._selected_id), None)
        if appt:
            AppointmentFormDialog(self, appt, self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("delete"), "Please select an appointment first.")
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            appointment_controller.delete(self._selected_id)
            self._selected_id = None
            self._load()


class AppointmentFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, appt, on_save):
        super().__init__(parent)
        self.appt = appt
        self.on_save = on_save
        self.title(lang.t("edit_appointment") if appt else lang.t("add_appointment"))
        self.geometry("460x400")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=16)
        frame.columnconfigure(0, weight=1)

        patients = patient_controller.get_all()
        doctors = doctor_controller.get_all()
        patient_names = [f"{p.id} — {p.full_name}" for p in patients]
        doctor_names = [f"{d.id} — {d.full_name}" for d in doctors]

        a = self.appt

        def label(text, row):
            ctk.CTkLabel(frame, text=text, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=12)).grid(row=row * 2, column=0, sticky="w", pady=(8, 0))

        def entry(default="", row=0):
            e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                             text_color=theme.get("entry_fg"),
                             border_color=theme.get("border"), height=36)
            e.insert(0, default)
            e.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(2, 0))
            return e

        label(lang.t("patient"), 0)
        self.patient_menu = ctk.CTkOptionMenu(frame, values=patient_names or ["—"])
        if a and a.patient:
            self.patient_menu.set(f"{a.patient_id} — {a.patient.full_name}")
        self.patient_menu.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self._patients = patients

        label(lang.t("doctor"), 1)
        self.doctor_menu = ctk.CTkOptionMenu(frame, values=doctor_names or ["—"])
        if a and a.doctor:
            self.doctor_menu.set(f"{a.doctor_id} — {a.doctor.full_name}")
        self.doctor_menu.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        self._doctors = doctors

        label(lang.t("appointment_date") + " (YYYY-MM-DD)", 2)
        self.date_e = entry(str(a.date) if a else str(datetime.date.today()), 2)

        label(lang.t("appointment_time") + " (HH:MM)", 3)
        self.time_e = entry(str(a.time)[:5] if a else "09:00", 3)

        label(lang.t("status"), 4)
        self.status_menu = ctk.CTkOptionMenu(frame, values=STATUSES)
        self.status_menu.set(a.status if a else "scheduled")
        self.status_menu.grid(row=9, column=0, sticky="ew", pady=(2, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=12)
        ctk.CTkButton(btn_frame, text=lang.t("save"),
                      fg_color=theme.get("accent"),
                      hover_color=theme.get("accent_hover"),
                      command=self._save).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text=lang.t("cancel"),
                      fg_color=theme.get("border"),
                      text_color=theme.get("text_primary"),
                      hover_color=theme.get("table_row_alt"),
                      command=self.destroy).pack(side="right")

    def _save(self):
        try:
            date = datetime.date.fromisoformat(self.date_e.get().strip())
        except ValueError:
            messagebox.showerror(lang.t("error"), "Date must be YYYY-MM-DD")
            return
        try:
            time_str = self.time_e.get().strip()
            h, m = time_str.split(":")
            time = datetime.time(int(h), int(m))
        except Exception:
            messagebox.showerror(lang.t("error"), "Time must be HH:MM")
            return

        # Extract patient/doctor IDs from option menu text
        p_str = self.patient_menu.get()
        d_str = self.doctor_menu.get()
        try:
            pid = int(p_str.split("—")[0].strip())
            did = int(d_str.split("—")[0].strip())
        except Exception:
            messagebox.showerror(lang.t("error"), "Please select a patient and doctor.")
            return

        exclude = self.appt.id if self.appt else None
        if appointment_controller.check_double_booking(did, date, time, exclude_id=exclude):
            messagebox.showerror(lang.t("error"), lang.t("double_booking"))
            return

        data = {
            "patient_id": pid,
            "doctor_id": did,
            "date": date,
            "time": time,
            "status": self.status_menu.get(),
        }
        if self.appt:
            appointment_controller.update(self.appt.id, data)
        else:
            appointment_controller.add(data)
        self.on_save()
        self.destroy()
