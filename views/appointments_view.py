"""Appointments management view."""

import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import appointment_controller, patient_controller, doctor_controller

STATUSES = ["scheduled", "completed", "cancelled"]

SEL_COLOR = "#1976d2"   # لون تمييز الصف المحدد


class AppointmentsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._row_frames = {}     # id → frame لتغيير اللون عند التحديد
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("appointments"),
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

        for label, cmd, color in [
            (lang.t("add"),    self._open_add,    theme.get("accent")),
            (lang.t("edit"),   self._open_edit,   theme.get("warning")),
            (lang.t("delete"), self._delete,      theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=90, height=38,
                          fg_color=color, hover_color=theme.get("accent_hover"),
                          corner_radius=8, font=ctk.CTkFont(size=13),
                          command=cmd).pack(side="right", padx=4)

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        headers = ["ID", lang.t("patient"), lang.t("doctor"),
                   lang.t("appointment_date"), lang.t("appointment_time"), lang.t("status")]
        widths   = [50, 180, 180, 120, 90, 110]

        hf = ctk.CTkFrame(card, fg_color=theme.get("table_header"), corner_radius=0)
        hf.pack(fill="x")
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=theme.get("text_primary")).grid(
                             row=0, column=i, padx=8, pady=10, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self._widths = widths

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._row_frames.clear()
        appts = appointment_controller.get_all()
        if not appts:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         font=ctk.CTkFont(size=13),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        status_colors = {
            "scheduled": theme.get("accent"),
            "completed": theme.get("success"),
            "cancelled": theme.get("danger"),
        }
        for idx, a in enumerate(appts):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=40)
            row.pack(fill="x")
            row.pack_propagate(False)
            self._row_frames[a.id] = (row, bg)

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
                             font=ctk.CTkFont(size=13)).grid(
                                 row=0, column=ci, padx=8, pady=0, sticky="w")
            aid = a.id
            row.bind("<Button-1>", lambda e, i=aid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=aid: self._select(i))

    def _select(self, aid):
        # أعد لون الصف السابق
        if self._selected_id and self._selected_id in self._row_frames:
            prev_row, prev_bg = self._row_frames[self._selected_id]
            try:
                prev_row.configure(fg_color=prev_bg)
            except Exception:
                pass
        self._selected_id = aid
        # لوّن الصف الجديد
        if aid in self._row_frames:
            row, _ = self._row_frames[aid]
            try:
                row.configure(fg_color=SEL_COLOR)
            except Exception:
                pass

    def _open_add(self):
        AppointmentFormDialog(self, None, self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("edit"), lang.t("select_appointment") if lang.t("select_appointment") != "select_appointment" else "Please select an appointment first.")
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


class TimePickerDialog(tk.Toplevel):
    """Simple time picker dialog (HH:MM) using Spinbox controls."""
    def __init__(self, parent, initial_time=None):
        super().__init__(parent)
        self.result = None
        self.title(lang.t("select_time") if hasattr(lang, 't') else "Select Time")
        self.resizable(False, False)
        self.grab_set()

        _is_dark = ctk.get_appearance_mode().lower() == "dark"
        _bg = "#2b2b2b" if _is_dark else "#f5f5f5"
        self.configure(bg=_bg)

        h_val = f"{initial_time.hour:02d}" if initial_time else "09"
        m_val = f"{initial_time.minute:02d}" if initial_time else "00"

        frm = tk.Frame(self, bg=_bg)
        frm.pack(padx=12, pady=12)

        tk.Label(frm, text=lang.t("hour") if lang.t("hour") != "hour" else "Hour", bg=_bg,
                 fg="#ffffff" if _is_dark else "#333333").grid(row=0, column=0)
        self._hour = tk.Spinbox(frm, from_=0, to=23, width=3, format="%02.0f")
        self._hour.delete(0, "end")
        self._hour.insert(0, h_val)
        self._hour.grid(row=1, column=0, padx=6)

        tk.Label(frm, text=":", bg=_bg,
                 fg="#ffffff" if _is_dark else "#333333").grid(row=1, column=1)

        tk.Label(frm, text=lang.t("minute") if lang.t("minute") != "minute" else "Minute", bg=_bg,
                 fg="#ffffff" if _is_dark else "#333333").grid(row=0, column=2)
        self._minute = tk.Spinbox(frm, from_=0, to=59, width=3, format="%02.0f")
        self._minute.delete(0, "end")
        self._minute.insert(0, m_val)
        self._minute.grid(row=1, column=2, padx=6)

        btns = tk.Frame(self, bg=_bg)
        btns.pack(pady=(8, 12))

        def _ok():
            try:
                h = int(self._hour.get())
                m = int(self._minute.get())
                self.result = datetime.time(h, m)
            except Exception:
                self.result = None
            self.destroy()

        def _cancel():
            self.result = None
            self.destroy()

        tk.Button(btns, text=lang.t("save"), command=_ok, padx=12, pady=6, bg="#1f6aa5", fg="white").pack(side="left", padx=6)
        tk.Button(btns, text=lang.t("cancel"), command=_cancel, padx=12, pady=6).pack(side="left", padx=6)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.wait_window()


class AppointmentFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, appt, on_save):
        super().__init__(parent)
        self.appt = appt
        self.on_save = on_save
        self.title(lang.t("edit_appointment") if appt else lang.t("add_appointment"))
        self.geometry("480x520")
        self.minsize(440, 480)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=16)
        scroll.columnconfigure(0, weight=1)

        patients = patient_controller.get_all()
        doctors  = doctor_controller.get_all()
        patient_names = [f"{p.id} — {p.full_name}" for p in patients]
        doctor_names  = [f"{d.id} — {d.full_name}" for d in doctors]
        self._patients = patients
        self._doctors  = doctors

        a = self.appt

        def lbl(text, row):
            ctk.CTkLabel(scroll, text=text, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=13)).grid(
                             row=row, column=0, sticky="w", pady=(10, 0))

        def entry_w(default="", row=0):
            e = ctk.CTkEntry(scroll, height=40,
                             fg_color=theme.get("entry_bg"),
                             text_color=theme.get("entry_fg"),
                             border_color=theme.get("border"),
                             font=ctk.CTkFont(size=13))
            e.insert(0, default)
            e.grid(row=row, column=0, sticky="ew", pady=(3, 0))
            return e

        # Patient
        lbl(lang.t("patient"), 0)
        self.patient_menu = ctk.CTkOptionMenu(
            scroll, values=patient_names or ["—"],
            height=40, font=ctk.CTkFont(size=13),
            fg_color=theme.get("entry_bg"),
            button_color=theme.get("accent"),
            text_color=theme.get("entry_fg"))
        if a and a.patient:
            self.patient_menu.set(f"{a.patient_id} — {a.patient.full_name}")
        self.patient_menu.grid(row=1, column=0, sticky="ew", pady=(3, 0))

        # Doctor
        lbl(lang.t("doctor"), 2)
        self.doctor_menu = ctk.CTkOptionMenu(
            scroll, values=doctor_names or ["—"],
            height=40, font=ctk.CTkFont(size=13),
            fg_color=theme.get("entry_bg"),
            button_color=theme.get("accent"),
            text_color=theme.get("entry_fg"))
        if a and a.doctor:
            self.doctor_menu.set(f"{a.doctor_id} — {a.doctor.full_name}")
        self.doctor_menu.grid(row=3, column=0, sticky="ew", pady=(3, 0))

        # Date
        lbl(lang.t("appointment_date") + " (YYYY-MM-DD)", 4)
        self.date_e = entry_w(str(a.date) if a else str(datetime.date.today()), 5)

        # Time
        lbl(lang.t("appointment_time") + " (HH:MM)", 6)
        # Time entry with picker button
        time_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        time_frame.grid(row=7, column=0, sticky="ew", pady=(3, 0))
        time_frame.columnconfigure(0, weight=1)
        self.time_e = ctk.CTkEntry(time_frame, height=40,
                     fg_color=theme.get("entry_bg"),
                     text_color=theme.get("entry_fg"),
                     border_color=theme.get("border"),
                     font=ctk.CTkFont(size=13))
        self.time_e.insert(0, str(a.time)[:5] if a else "09:00")
        self.time_e.grid(row=0, column=0, sticky="ew")
        pick_btn = ctk.CTkButton(time_frame, text="⌚", width=44, height=40,
                     fg_color=theme.get("accent"),
                     hover_color=theme.get("accent_hover"),
                     command=self._open_time_picker)
        pick_btn.grid(row=0, column=1, padx=(8, 0))

        # Status
        lbl(lang.t("status"), 8)
        self.status_menu = ctk.CTkOptionMenu(
            scroll, values=STATUSES,
            height=40, font=ctk.CTkFont(size=13),
            fg_color=theme.get("entry_bg"),
            button_color=theme.get("accent"),
            text_color=theme.get("entry_fg"))
        self.status_menu.set(a.status if a else "scheduled")
        self.status_menu.grid(row=9, column=0, sticky="ew", pady=(3, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(4, 24))
        ctk.CTkButton(btn_frame, text=lang.t("save"),
                      height=42, corner_radius=8,
                      fg_color=theme.get("accent"),
                      hover_color=theme.get("accent_hover"),
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._save).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text=lang.t("cancel"),
                      height=42, corner_radius=8,
                      fg_color=theme.get("border"),
                      text_color=theme.get("text_primary"),
                      hover_color=theme.get("table_row_alt"),
                      font=ctk.CTkFont(size=13),
                      command=self.destroy).pack(side="right")

    def _open_time_picker(self):
        """Open the TimePickerDialog and write the result into the time entry."""
        try:
            cur = self.time_e.get().strip()
            h, m = cur.split(":")
            init = datetime.time(int(h), int(m))
        except Exception:
            init = None
        dlg = TimePickerDialog(self, initial_time=init)
        if getattr(dlg, "result", None):
            t = dlg.result
            self.time_e.delete(0, tk.END)
            self.time_e.insert(0, f"{t.hour:02d}:{t.minute:02d}")

    def _save(self):
        try:
            date = datetime.date.fromisoformat(self.date_e.get().strip())
        except ValueError:
            messagebox.showerror(lang.t("error"), "Date must be YYYY-MM-DD")
            return
        try:
            h, m = self.time_e.get().strip().split(":")
            time = datetime.time(int(h), int(m))
        except Exception:
            messagebox.showerror(lang.t("error"), "Time must be HH:MM")
            return
        try:
            pid = int(self.patient_menu.get().split("—")[0].strip())
            did = int(self.doctor_menu.get().split("—")[0].strip())
        except Exception:
            messagebox.showerror(lang.t("error"), "Please select a patient and doctor.")
            return
        exclude = self.appt.id if self.appt else None
        if appointment_controller.check_double_booking(did, date, time, exclude_id=exclude):
            messagebox.showerror(lang.t("error"), lang.t("double_booking"))
            return
        data = {
            "patient_id": pid,
            "doctor_id":  did,
            "date":   date,
            "time":   time,
            "status": self.status_menu.get(),
        }
        if self.appt:
            appointment_controller.update(self.appt.id, data)
        else:
            appointment_controller.add(data)
        self.on_save()
        self.destroy()
