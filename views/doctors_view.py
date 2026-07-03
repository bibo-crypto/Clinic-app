"""Doctors management view."""

import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import doctor_controller


class DoctorsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("doctors"),
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

        headers = ["ID", lang.t("doctor_name"), lang.t("specialization"),
                   lang.t("phone"), lang.t("consultation_fee")]
        widths = [50, 220, 180, 140, 130]

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
        doctors = doctor_controller.get_all()
        if not doctors:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, d in enumerate(doctors):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            vals = [str(d.id), d.full_name, d.specialization or "", d.phone or "", f"${d.consultation_fee:.2f}"]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=theme.get("text_primary"),
                             font=ctk.CTkFont(size=12)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            did = d.id
            row.bind("<Button-1>", lambda e, i=did: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=did: self._select(i))

    def _select(self, did):
        self._selected_id = did

    def _open_add(self):
        DoctorFormDialog(self, None, self._load)

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("edit"), lang.t("select_doctor"))
            return
        d = doctor_controller.get_by_id(self._selected_id)
        if d:
            DoctorFormDialog(self, d, self._load)

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("delete"), lang.t("select_doctor"))
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            doctor_controller.delete(self._selected_id)
            self._selected_id = None
            self._load()


class DoctorFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, doctor, on_save):
        super().__init__(parent)
        self.doctor = doctor
        self.on_save = on_save
        self.title(lang.t("edit_doctor") if doctor else lang.t("add_doctor"))
        self.geometry("420x340")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=16)
        frame.columnconfigure(0, weight=1)

        def entry(default=""):
            e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                             text_color=theme.get("entry_fg"),
                             border_color=theme.get("border"), height=36)
            e.insert(0, default)
            return e

        d = self.doctor
        rows = [
            (lang.t("doctor_name"), entry(d.full_name if d else "")),
            (lang.t("specialization"), entry(d.specialization if d else "")),
            (lang.t("phone"), entry(d.phone if d else "")),
            (lang.t("consultation_fee"), entry(str(d.consultation_fee) if d else "0")),
        ]
        self._widgets = {}
        for i, (label, widget) in enumerate(rows):
            ctk.CTkLabel(frame, text=label, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=12)).grid(row=i * 2, column=0, sticky="w", pady=(8, 0))
            widget.grid(row=i * 2 + 1, column=0, sticky="ew", pady=(2, 0))
            self._widgets[label] = widget

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
        widgets = list(self._widgets.values())
        name = widgets[0].get().strip()
        if not name:
            messagebox.showerror(lang.t("error"), lang.t("required_field"))
            return
        try:
            fee = float(widgets[3].get().strip() or "0")
        except ValueError:
            fee = 0.0
        data = {
            "full_name": name,
            "specialization": widgets[1].get().strip(),
            "phone": widgets[2].get().strip(),
            "consultation_fee": fee,
        }
        if self.doctor:
            doctor_controller.update(self.doctor.id, data)
        else:
            doctor_controller.add(data)
        self.on_save()
        self.destroy()
