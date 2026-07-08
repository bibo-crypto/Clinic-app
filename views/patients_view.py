"""Patients management view."""

import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import patient_controller

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
SEL_COLOR   = "#1976d2"


# ── Date Picker Dialog ──────────────────────────────────────────────────────────

class DatePickerDialog(tk.Toplevel):
    """منتقي تاريخ متوافق بصرياً مع customtkinter."""

    def __init__(self, parent, initial_date=None):
        super().__init__(parent)
        self.result = None
        self.title(lang.t("select_date"))
        self.resizable(False, False)
        self.grab_set()

        _is_dark = ctk.get_appearance_mode().lower() == "dark"
        _bg = "#2b2b2b" if _is_dark else "#f5f5f5"
        self.configure(bg=_bg)

        try:
            import tkinter.font as tkfont
            tkfont.nametofont("TkDefaultFont").configure(family="Segoe UI", size=11)
        except Exception:
            pass

        try:
            from tkcalendar import Calendar
            today = initial_date or datetime.date.today()
            cal = Calendar(
                self,
                selectmode="day",
                year=today.year, month=today.month, day=today.day,
                date_pattern="yyyy-mm-dd",
                font=("Segoe UI", 10),
                background="#1f6aa5", foreground="white",
                headersbackground="#144870", headersforeground="white",
                selectbackground="#f59e0b", selectforeground="black",
                normalbackground="#2b2b2b" if _is_dark else "#ffffff",
                normalforeground="#ffffff" if _is_dark else "#1a1a1a",
                weekendforeground="#f59e0b",
            )
            cal.pack(padx=14, pady=14)

            btn_frame = tk.Frame(self, bg=_bg)
            btn_frame.pack(pady=(0, 14))

            _c_bg = "#444444" if _is_dark else "#dddddd"
            _c_fg = "#ffffff" if _is_dark else "#333333"

            def _select():
                try:
                    self.result = datetime.date.fromisoformat(cal.get_date())
                except ValueError:
                    self.result = None
                self.destroy()

            tk.Button(btn_frame, text=lang.t("save"),
                      bg="#1f6aa5", fg="white", padx=24, pady=6,
                      relief="flat", cursor="hand2",
                      font=("Segoe UI", 11, "bold"),
                      command=_select).pack(side="left", padx=6)
            tk.Button(btn_frame, text=lang.t("cancel"),
                      bg=_c_bg, fg=_c_fg, padx=24, pady=6,
                      relief="flat", cursor="hand2",
                      font=("Segoe UI", 11),
                      command=self.destroy).pack(side="left", padx=6)

        except ImportError:
            _fg = "#ffffff" if _is_dark else "#333333"
            tk.Label(self, text="tkcalendar غير مثبتة\npip install tkcalendar",
                     bg=_bg, fg=_fg, font=("Segoe UI", 12), padx=20, pady=20).pack()
            tk.Button(self, text=lang.t("close"), command=self.destroy).pack(pady=8)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.wait_window()


# ── Patients Main View ──────────────────────────────────────────────────────────

class PatientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id  = None
        self._row_frames   = {}
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("patients"),
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(top, width=240, placeholder_text=lang.t("search"),
                     textvariable=self.search_var, height=38,
                     fg_color=theme.get("entry_bg"),
                     text_color=theme.get("entry_fg"),
                     border_color=theme.get("border")).pack(side="right", padx=(0, 8))

        for label, cmd, color in [
            (lang.t("add"),    self._open_add,  theme.get("accent")),
            (lang.t("edit"),   self._open_edit, theme.get("warning")),
            (lang.t("delete"), self._delete,    theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=90, height=38,
                          fg_color=color, hover_color=theme.get("accent_hover"),
                          corner_radius=8, font=ctk.CTkFont(size=13),
                          command=cmd).pack(side="right", padx=4)

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        headers = ["ID", lang.t("full_name"), lang.t("gender"),
                   lang.t("date_of_birth"), lang.t("phone"), lang.t("blood_type")]
        widths   = [50, 200, 90, 130, 140, 80]

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
        q = self.search_var.get().strip()
        self._patients = patient_controller.search(q) if q else patient_controller.get_all()
        if not self._patients:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         font=ctk.CTkFont(size=13),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, p in enumerate(self._patients):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=40)
            row.pack(fill="x")
            row.pack_propagate(False)
            self._row_frames[p.id] = (row, bg)
            vals = [str(p.id), p.full_name, p.gender or "",
                    str(p.date_of_birth or ""), p.phone or "", p.blood_type or ""]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=theme.get("text_primary"),
                             font=ctk.CTkFont(size=13)).grid(
                                 row=0, column=ci, padx=8, pady=0, sticky="w")
            pid = p.id
            row.bind("<Button-1>", lambda e, i=pid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=pid: self._select(i))

    def _select(self, pid):
        if self._selected_id and self._selected_id in self._row_frames:
            prev_row, prev_bg = self._row_frames[self._selected_id]
            try: prev_row.configure(fg_color=prev_bg)
            except Exception: pass
        self._selected_id = pid
        if pid in self._row_frames:
            row, _ = self._row_frames[pid]
            try: row.configure(fg_color=SEL_COLOR)
            except Exception: pass

    def _open_add(self):
        PatientFormDialog(self, None, self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("edit"), lang.t("select_patient"))
            return
        p = patient_controller.get_by_id(self._selected_id)
        if p:
            PatientFormDialog(self, p, self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("delete"), lang.t("select_patient"))
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            patient_controller.delete(self._selected_id)
            self._selected_id = None
            self._load()


# ── Patient Form Dialog ─────────────────────────────────────────────────────────

class PatientFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, patient, on_save):
        super().__init__(parent)
        self.patient   = patient
        self.on_save   = on_save
        self._dob_value = patient.date_of_birth if patient and patient.date_of_birth else None
        self.title(lang.t("edit_patient") if patient else lang.t("add_patient"))
        self.geometry("540x660")
        self.minsize(500, 580)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=16)
        scroll.columnconfigure(0, weight=1)
        p = self.patient

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

        lbl(lang.t("full_name"), 0)
        self.name_e = entry_w(p.full_name if p else "", 1)

        # تاريخ الميلاد — Date Picker
        lbl(lang.t("date_of_birth"), 2)
        dob_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        dob_frame.grid(row=3, column=0, sticky="ew", pady=(3, 0))
        dob_frame.columnconfigure(0, weight=1)

        self.dob_label = ctk.CTkLabel(
            dob_frame,
            text=str(self._dob_value) if self._dob_value else lang.t("select_date"),
            anchor="w", height=40,
            fg_color=theme.get("entry_bg"),
            text_color=theme.get("entry_fg") if self._dob_value else theme.get("text_secondary"),
            corner_radius=8,
            font=ctk.CTkFont(size=13),
        )
        self.dob_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(dob_frame, text="📅", width=44, height=40,
                      corner_radius=8,
                      fg_color=theme.get("accent"),
                      hover_color=theme.get("accent_hover"),
                      font=ctk.CTkFont(size=16),
                      command=self._pick_dob).grid(row=0, column=1)

        lbl(lang.t("phone"),   4); self.phone_e   = entry_w(p.phone   if p else "", 5)
        lbl(lang.t("address"), 6); self.address_e = entry_w(p.address if p else "", 7)

        # الجنس
        lbl(lang.t("gender"), 8)
        self.gender_var = ctk.StringVar(value=p.gender if p else "Male")
        gf = ctk.CTkFrame(scroll, fg_color="transparent")
        gf.grid(row=9, column=0, sticky="w", pady=(3, 0))
        ctk.CTkRadioButton(gf, text=lang.t("male"),
                           variable=self.gender_var, value="Male",
                           font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(gf, text=lang.t("female"),
                           variable=self.gender_var, value="Female",
                           font=ctk.CTkFont(size=13)).pack(side="left")

        # فصيلة الدم
        lbl(lang.t("blood_type"), 10)
        self.blood_menu = ctk.CTkOptionMenu(
            scroll, values=BLOOD_TYPES, height=40,
            fg_color=theme.get("entry_bg"),
            button_color=theme.get("accent"),
            button_hover_color=theme.get("accent_hover"),
            text_color=theme.get("entry_fg"),
            font=ctk.CTkFont(size=13))
        self.blood_menu.set(p.blood_type if p and p.blood_type else "A+")
        self.blood_menu.grid(row=11, column=0, sticky="w", pady=(3, 0))

        lbl(lang.t("allergies"),    12); self.allergies_e = entry_w(p.allergies    if p else "", 13)
        lbl(lang.t("medical_notes"),14); self.notes_e     = entry_w(p.medical_notes if p else "", 15)

        # الأزرار
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

    def _pick_dob(self):
        dlg = DatePickerDialog(self, self._dob_value)
        if dlg.result:
            self._dob_value = dlg.result
            self.dob_label.configure(
                text=str(self._dob_value),
                text_color=theme.get("entry_fg"))

    def _save(self):
        name = self.name_e.get().strip()
        if not name:
            messagebox.showerror(lang.t("error"), lang.t("required_field"))
            return
        data = {
            "full_name":    name,
            "gender":       self.gender_var.get(),
            "date_of_birth":self._dob_value,
            "phone":        self.phone_e.get().strip(),
            "address":      self.address_e.get().strip(),
            "blood_type":   self.blood_menu.get(),
            "allergies":    self.allergies_e.get().strip(),
            "medical_notes":self.notes_e.get().strip(),
        }
        if self.patient:
            patient_controller.update(self.patient.id, data)
        else:
            patient_controller.add(data)
        self.on_save()
        self.destroy()
