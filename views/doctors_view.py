"""Doctors management view."""

import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import doctor_controller

SEL_COLOR = "#1976d2"

# ── التخصصات الطبية ────────────────────────────────────────────────────────────
_SPECIALIZATIONS = [
    ("internal",        "Internal Medicine",         "الباطنة"),
    ("cardiology",      "Cardiology",                "أمراض القلب"),
    ("dermatology",     "Dermatology",               "الأمراض الجلدية"),
    ("pediatrics",      "Pediatrics",                "طب الأطفال"),
    ("gynecology",      "Gynecology & Obstetrics",   "أمراض النساء والتوليد"),
    ("orthopedics",     "Orthopedics",               "العظام والمفاصل"),
    ("ent",             "ENT (Ear, Nose & Throat)",  "أنف وأذن وحنجرة"),
    ("ophthalmology",   "Ophthalmology",             "طب العيون"),
    ("neurology",       "Neurology",                 "المخ والأعصاب"),
    ("psychiatry",      "Psychiatry",                "الطب النفسي"),
    ("urology",         "Urology",                   "المسالك البولية"),
    ("gastro",          "Gastroenterology",          "الجهاز الهضمي"),
    ("pulmonology",     "Pulmonology",               "أمراض الصدر والتنفس"),
    ("endocrinology",   "Endocrinology",             "الغدد الصماء والسكر"),
    ("oncology",        "Oncology",                  "أورام"),
    ("surgery_general", "General Surgery",           "الجراحة العامة"),
    ("surgery_plastic", "Plastic Surgery",           "الجراحة التجميلية"),
    ("surgery_cardio",  "Cardiac Surgery",           "جراحة القلب"),
    ("surgery_neuro",   "Neurosurgery",              "جراحة المخ والأعصاب"),
    ("radiology",       "Radiology",                 "الأشعة التشخيصية"),
    ("anesthesia",      "Anesthesiology",            "التخدير والعناية المركزة"),
    ("emergency",       "Emergency Medicine",        "طب الطوارئ"),
    ("family",          "Family Medicine",           "طب الأسرة"),
    ("rheumatology",    "Rheumatology",              "الروماتيزم"),
    ("nephrology",      "Nephrology",                "الكلى"),
    ("hematology",      "Hematology",                "أمراض الدم"),
    ("dentistry",       "Dentistry",                 "طب الأسنان"),
    ("nutrition",       "Clinical Nutrition",        "التغذية العلاجية"),
    ("physical",        "Physical Therapy",          "العلاج الطبيعي"),
    ("other",           "Other",                     "أخرى"),
]

def _spec_labels():
    ar = lang.current() == "ar"
    return [s[2] if ar else s[1] for s in _SPECIALIZATIONS]

def _label_to_key(label):
    for key, en, ar in _SPECIALIZATIONS:
        if label in (en, ar):
            return key
    return label

def _key_to_label(key):
    ar = lang.current() == "ar"
    for k, en, ar_name in _SPECIALIZATIONS:
        if k == key:
            return ar_name if ar else en
    return key


# ── Doctors Main View ───────────────────────────────────────────────────────────

class DoctorsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._row_frames  = {}
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("doctors"),
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

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

        headers = ["ID", lang.t("doctor_name"), lang.t("specialization"),
                   lang.t("phone"), lang.t("consultation_fee")]
        widths   = [50, 200, 220, 140, 120]

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
        doctors = doctor_controller.get_all()
        if not doctors:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         font=ctk.CTkFont(size=13),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, d in enumerate(doctors):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=40)
            row.pack(fill="x")
            row.pack_propagate(False)
            self._row_frames[d.id] = (row, bg)
            vals = [str(d.id), d.full_name,
                    _key_to_label(d.specialization or ""),
                    d.phone or "", f"${d.consultation_fee:.2f}"]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=theme.get("text_primary"),
                             font=ctk.CTkFont(size=13)).grid(
                                 row=0, column=ci, padx=8, pady=0, sticky="w")
            did = d.id
            row.bind("<Button-1>", lambda e, i=did: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=did: self._select(i))

    def _select(self, did):
        if self._selected_id and self._selected_id in self._row_frames:
            prev_row, prev_bg = self._row_frames[self._selected_id]
            try: prev_row.configure(fg_color=prev_bg)
            except Exception: pass
        self._selected_id = did
        if did in self._row_frames:
            row, _ = self._row_frames[did]
            try: row.configure(fg_color=SEL_COLOR)
            except Exception: pass

    def _open_add(self):
        DoctorFormDialog(self, None, self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("edit"), lang.t("select_doctor")
                                if lang.t("select_doctor") != "select_doctor"
                                else "Please select a doctor first.")
            return
        doctors = doctor_controller.get_all()
        d = next((x for x in doctors if x.id == self._selected_id), None)
        if d:
            DoctorFormDialog(self, d, self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("delete"), "Please select a doctor first.")
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            doctor_controller.delete(self._selected_id)
            self._selected_id = None
            self._load()


# ── Doctor Form Dialog ──────────────────────────────────────────────────────────

class DoctorFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, doctor, on_save):
        super().__init__(parent)
        self.doctor  = doctor
        self.on_save = on_save
        self.title(lang.t("edit_doctor") if doctor else lang.t("add_doctor"))
        self.geometry("480x540")
        self.minsize(440, 500)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=16)
        scroll.columnconfigure(0, weight=1)
        d = self.doctor

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

        lbl(lang.t("doctor_name"), 0)
        self.name_e = entry_w(d.full_name if d else "", 1)

        lbl(lang.t("specialization"), 2)
        spec_labels = _spec_labels()
        current_label = _key_to_label(d.specialization) if d and d.specialization else spec_labels[0]
        if current_label not in spec_labels:
            spec_labels = [current_label] + spec_labels
        self.spec_menu = ctk.CTkOptionMenu(
            scroll, values=spec_labels, height=40,
            fg_color=theme.get("entry_bg"),
            button_color=theme.get("accent"),
            button_hover_color=theme.get("accent_hover"),
            text_color=theme.get("entry_fg"),
            dropdown_fg_color=theme.get("card_bg"),
            dropdown_text_color=theme.get("text_primary"),
            font=ctk.CTkFont(size=13),
            dynamic_resizing=False)
        self.spec_menu.set(current_label)
        self.spec_menu.grid(row=3, column=0, sticky="ew", pady=(3, 0))

        lbl(lang.t("phone"), 4)
        self.phone_e = entry_w(d.phone if d else "", 5)

        lbl(lang.t("consultation_fee"), 6)
        self.fee_e = entry_w(str(int(d.consultation_fee)) if d else "0", 7)

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

    def _save(self):
        name = self.name_e.get().strip()
        if not name:
            messagebox.showerror(lang.t("error"), lang.t("required_field"))
            return
        try:
            fee = float(self.fee_e.get().strip() or "0")
        except ValueError:
            fee = 0.0
        data = {
            "full_name":       name,
            "specialization":  _label_to_key(self.spec_menu.get()),
            "phone":           self.phone_e.get().strip(),
            "consultation_fee":fee,
        }
        if self.doctor:
            doctor_controller.update(self.doctor.id, data)
        else:
            doctor_controller.add(data)
        self.on_save()
        self.destroy()
