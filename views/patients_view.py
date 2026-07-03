"""Patients management view."""

import datetime
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import patient_controller


BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


class PatientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._patients = []
        self._selected_id = None
        self._build()
        self._load()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("patients"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        search = ctk.CTkEntry(top, width=240, placeholder_text=lang.t("search"),
                              textvariable=self.search_var,
                              fg_color=theme.get("entry_bg"),
                              text_color=theme.get("entry_fg"),
                              border_color=theme.get("border"))
        search.pack(side="right", padx=(0, 8))

        for label, cmd, color in [
            (lang.t("add"), self._open_add, theme.get("accent")),
            (lang.t("edit"), self._open_edit, theme.get("warning")),
            (lang.t("delete"), self._delete, theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=90, fg_color=color,
                          hover_color=theme.get("accent_hover"),
                          corner_radius=8, command=cmd).pack(side="right", padx=4)

        # Table card
        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        headers = ["ID", lang.t("full_name"), lang.t("gender"), lang.t("date_of_birth"),
                   lang.t("phone"), lang.t("blood_type")]
        widths = [50, 200, 80, 120, 130, 80]

        header_frame = ctk.CTkFrame(card, fg_color=theme.get("table_header"), corner_radius=0)
        header_frame.pack(fill="x")
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(header_frame, text=h, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=theme.get("text_primary")).grid(row=0, column=i, padx=8, pady=8, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self._widths = widths

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        q = self.search_var.get().strip()
        self._patients = patient_controller.search(q) if q else patient_controller.get_all()
        if not self._patients:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, p in enumerate(self._patients):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            vals = [str(p.id), p.full_name, p.gender or "", str(p.date_of_birth or ""), p.phone or "", p.blood_type or ""]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=theme.get("text_primary"),
                             font=ctk.CTkFont(size=12)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            pid = p.id
            row.bind("<Button-1>", lambda e, i=pid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=pid: self._select(i))

    def _select(self, patient_id):
        self._selected_id = patient_id

    # ── CRUD ──────────────────────────────────────────────────────────────────

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


# ── Patient Form Dialog ────────────────────────────────────────────────────────

class PatientFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, patient, on_save):
        super().__init__(parent)
        self.patient = patient
        self.on_save = on_save
        self.title(lang.t("edit_patient") if patient else lang.t("add_patient"))
        self.geometry("520x580")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=16)

        def field(label, row, widget_fn):
            ctk.CTkLabel(frame, text=label, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=12)).grid(row=row * 2, column=0, sticky="w", pady=(8, 0))
            w = widget_fn()
            w.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(2, 0))
            return w

        frame.columnconfigure(0, weight=1)

        def entry(default=""):
            e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                             text_color=theme.get("entry_fg"),
                             border_color=theme.get("border"), height=36)
            e.insert(0, default)
            return e

        p = self.patient
        self.name_e = field(lang.t("full_name"), 0, lambda: entry(p.full_name if p else ""))
        self.dob_e = field(lang.t("date_of_birth") + " (YYYY-MM-DD)", 1,
                           lambda: entry(str(p.date_of_birth) if p and p.date_of_birth else ""))
        self.phone_e = field(lang.t("phone"), 2, lambda: entry(p.phone if p else ""))
        self.address_e = field(lang.t("address"), 3, lambda: entry(p.address if p else ""))

        # Gender
        ctk.CTkLabel(frame, text=lang.t("gender"), anchor="w",
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).grid(row=8, column=0, sticky="w", pady=(8, 0))
        self.gender_var = ctk.StringVar(value=p.gender if p else lang.t("male"))
        g_frame = ctk.CTkFrame(frame, fg_color="transparent")
        g_frame.grid(row=9, column=0, sticky="w")
        ctk.CTkRadioButton(g_frame, text=lang.t("male"), variable=self.gender_var, value="Male").pack(side="left", padx=8)
        ctk.CTkRadioButton(g_frame, text=lang.t("female"), variable=self.gender_var, value="Female").pack(side="left")

        # Blood type
        ctk.CTkLabel(frame, text=lang.t("blood_type"), anchor="w",
                     text_color=theme.get("text_secondary"),
                     font=ctk.CTkFont(size=12)).grid(row=10, column=0, sticky="w", pady=(8, 0))
        self.blood_menu = ctk.CTkOptionMenu(frame, values=BLOOD_TYPES)
        self.blood_menu.set(p.blood_type if p and p.blood_type else "A+")
        self.blood_menu.grid(row=11, column=0, sticky="w")

        self.allergies_e = field(lang.t("allergies"), 6, lambda: entry(p.allergies if p else ""))
        self.notes_e = field(lang.t("medical_notes"), 7, lambda: entry(p.medical_notes if p else ""))

        # Buttons
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
        dob_str = self.dob_e.get().strip()
        dob = None
        if dob_str:
            try:
                dob = datetime.date.fromisoformat(dob_str)
            except ValueError:
                messagebox.showerror(lang.t("error"), "Date format must be YYYY-MM-DD")
                return

        data = {
            "full_name": self.name_e.get().strip(),
            "gender": self.gender_var.get(),
            "date_of_birth": dob,
            "phone": self.phone_e.get().strip(),
            "address": self.address_e.get().strip(),
            "blood_type": self.blood_menu.get(),
            "allergies": self.allergies_e.get().strip(),
            "medical_notes": self.notes_e.get().strip(),
        }
        if not data["full_name"]:
            messagebox.showerror(lang.t("error"), lang.t("required_field"))
            return
        if self.patient:
            patient_controller.update(self.patient.id, data)
        else:
            patient_controller.add(data)
        self.on_save()
        self.destroy()
