"""Medical Records view — per-patient history."""

import datetime
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import medical_record_controller, patient_controller


class MedicalRecordsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_patient_id = None
        self._selected_record_id = None
        self._row_frames = {}
        self._build()

    def _build(self):
        # Left panel — patient selector
        pane = ctk.CTkFrame(self, fg_color="transparent")
        pane.pack(fill="both", expand=True)
        pane.columnconfigure(0, weight=1)
        pane.columnconfigure(1, weight=3)
        pane.rowconfigure(0, weight=1)

        left = ctk.CTkFrame(pane, fg_color=theme.get("card_bg"), corner_radius=12)
        left.grid(row=0, column=0, padx=(28, 8), pady=(24, 24), sticky="nsew")

        ctk.CTkLabel(left, text=lang.t("patients"),
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.get("text_primary")).pack(padx=12, pady=(12, 4), anchor="w")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_patients())
        ctk.CTkEntry(left, textvariable=self.search_var,
                     placeholder_text=lang.t("search"),
                     fg_color=theme.get("entry_bg"),
                     text_color=theme.get("entry_fg"),
                     border_color=theme.get("border")).pack(fill="x", padx=12, pady=(0, 8))

        self.patient_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.patient_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        # Right panel — records
        right = ctk.CTkFrame(pane, fg_color="transparent")
        right.grid(row=0, column=1, padx=(0, 28), pady=(24, 24), sticky="nsew")

        top = ctk.CTkFrame(right, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(top, text=lang.t("medical_records"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")
        for label, cmd, color in [
            (lang.t("add_record"), self._open_add, theme.get("accent")),
            (lang.t("edit"), self._open_edit, theme.get("warning")),
            (lang.t("delete"), self._delete_record, theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=100, fg_color=color,
                          hover_color=theme.get("accent_hover"),
                          corner_radius=8, command=cmd).pack(side="right", padx=4)

        record_card = ctk.CTkFrame(right, fg_color=theme.get("card_bg"), corner_radius=12)
        record_card.pack(fill="both", expand=True)

        headers = ["ID", lang.t("visit_date"), lang.t("complaint"), lang.t("diagnosis")]
        widths = [50, 110, 220, 220]
        hf = ctk.CTkFrame(record_card, fg_color=theme.get("table_header"), corner_radius=0)
        hf.pack(fill="x")
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=theme.get("text_primary")).grid(row=0, column=i, padx=8, pady=8, sticky="w")

        self.record_scroll = ctk.CTkScrollableFrame(record_card, fg_color="transparent")
        self.record_scroll.pack(fill="both", expand=True)
        self._widths = widths

        self._load_patients()

    def _load_patients(self):
        for w in self.patient_scroll.winfo_children():
            w.destroy()
        q = self.search_var.get().strip()
        patients = patient_controller.search(q) if q else patient_controller.get_all()
        for p in patients:
            btn = ctk.CTkButton(
                self.patient_scroll,
                text=p.full_name,
                fg_color="transparent",
                text_color=theme.get("text_primary"),
                hover_color=theme.get("table_row_alt"),
                anchor="w",
                corner_radius=6,
                command=lambda pid=p.id: self._select_patient(pid),
            )
            btn.pack(fill="x", padx=4, pady=2)

    def _select_patient(self, patient_id):
        self._selected_patient_id = patient_id
        self._selected_record_id = None
        self._load_records()

    def _load_records(self):
        for w in self.record_scroll.winfo_children():
            w.destroy()
        self._row_frames.clear()
        if not self._selected_patient_id:
            return
        records = medical_record_controller.get_by_patient(self._selected_patient_id)
        if not records:
            ctk.CTkLabel(self.record_scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, r in enumerate(records):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.record_scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            vals = [str(r.id), str(r.visit_date), r.complaint[:40], r.diagnosis[:40]]
            for ci, (val, w) in enumerate(zip(vals, self._widths)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=theme.get("text_primary"),
                             font=ctk.CTkFont(size=13)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            self._row_frames[r.id] = (row, bg)
            rid = r.id
            row.bind("<Button-1>", lambda e, i=rid: self._select_record(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=rid: self._select_record(i))

    def _select_record(self, rid):
        if self._selected_record_id and self._selected_record_id in self._row_frames:
            prev_row, prev_bg = self._row_frames[self._selected_record_id]
            try: prev_row.configure(fg_color=prev_bg)
            except Exception: pass
        self._selected_record_id = rid
        if rid in self._row_frames:
            row, _ = self._row_frames[rid]
            try: row.configure(fg_color="#1976d2")
            except Exception: pass

    def _open_add(self):
        if not self._selected_patient_id:
            messagebox.showinfo(lang.t("add_record"), lang.t("select_patient"))
            return
        RecordFormDialog(self, self._selected_patient_id, None, self._load_records)

    def _open_edit(self):
        if not self._selected_record_id:
            messagebox.showinfo(lang.t("edit"), "Please select a record.")
            return
        records = medical_record_controller.get_by_patient(self._selected_patient_id)
        rec = next((r for r in records if r.id == self._selected_record_id), None)
        if rec:
            RecordFormDialog(self, self._selected_patient_id, rec, self._load_records)

    def _delete_record(self):
        if not self._selected_record_id:
            messagebox.showinfo(lang.t("delete"), "Please select a record.")
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            medical_record_controller.delete(self._selected_record_id)
            self._selected_record_id = None
            self._load_records()


class RecordFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, patient_id, record, on_save):
        super().__init__(parent)
        self.patient_id = patient_id
        self.record = record
        self.on_save = on_save
        self.title(lang.t("add_record") if not record else lang.t("edit"))
        self.geometry("520x560")
        self.minsize(480, 520)
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=16)
        frame.columnconfigure(0, weight=1)

        r = self.record

        def labeled_entry(label, row, default="", height=36):
            ctk.CTkLabel(frame, text=label, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=13)).grid(row=row * 2, column=0, sticky="w", pady=(8, 0))
            if height > 36:
                e = ctk.CTkTextbox(frame, height=height,
                                   fg_color=theme.get("entry_bg"),
                                   text_color=theme.get("entry_fg"))
                e.insert("1.0", default)
            else:
                e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                                 text_color=theme.get("entry_fg"),
                                 border_color=theme.get("border"), height=36)
                e.insert(0, default)
            e.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(2, 0))
            return e

        self.date_e = labeled_entry(lang.t("visit_date") + " (YYYY-MM-DD)", 0,
                                    str(r.visit_date) if r else str(datetime.date.today()))
        self.complaint_e = labeled_entry(lang.t("complaint"), 1, r.complaint if r else "", height=70)
        self.diagnosis_e = labeled_entry(lang.t("diagnosis"), 2, r.diagnosis if r else "", height=70)
        self.prescription_e = labeled_entry(lang.t("prescription"), 3, r.prescription if r else "", height=70)
        self.notes_e = labeled_entry(lang.t("notes"), 4, r.notes if r else "", height=56)

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

    def _get_text(self, w):
        if isinstance(w, ctk.CTkTextbox):
            return w.get("1.0", "end").strip()
        return w.get().strip()

    def _save(self):
        try:
            visit_date = datetime.date.fromisoformat(self.date_e.get().strip())
        except ValueError:
            messagebox.showerror(lang.t("error"), "Date must be YYYY-MM-DD")
            return
        data = {
            "patient_id": self.patient_id,
            "visit_date": visit_date,
            "complaint": self._get_text(self.complaint_e),
            "diagnosis": self._get_text(self.diagnosis_e),
            "prescription": self._get_text(self.prescription_e),
            "notes": self._get_text(self.notes_e),
        }
        if self.record:
            medical_record_controller.update(self.record.id, data)
        else:
            medical_record_controller.add(data)
        self.on_save()
        self.destroy()
