"""Billing / Invoice view."""

import json
import datetime
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import billing_controller, patient_controller, doctor_controller


class BillingView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(top, text=lang.t("billing"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(side="left")

        for label, cmd, color in [
            (lang.t("create_invoice"), self._open_add, theme.get("accent")),
            (lang.t("mark_paid"), self._mark_paid, theme.get("success")),
            (lang.t("delete"), self._delete, theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=110, fg_color=color,
                          hover_color=theme.get("accent_hover"),
                          corner_radius=8, command=cmd).pack(side="right", padx=4)

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        headers = ["#", lang.t("patient"), lang.t("invoice_number"),
                   lang.t("visit_date"), lang.t("total_amount"), lang.t("payment_status")]
        widths = [40, 180, 80, 110, 110, 100]

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
        invoices = billing_controller.get_all()
        if not invoices:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        for idx, inv in enumerate(invoices):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            paid_text = lang.t("paid") if inv.is_paid else lang.t("unpaid")
            paid_color = theme.get("success") if inv.is_paid else theme.get("danger")
            vals = [
                str(idx + 1),
                inv.patient.full_name if inv.patient else "",
                f"INV-{inv.id:04d}",
                str(inv.invoice_date),
                f"${inv.total_amount:.2f}",
                paid_text,
            ]
            colors_list = [
                theme.get("text_primary")] * 5 + [paid_color]
            for ci, (val, w, color) in enumerate(zip(vals, self._widths, colors_list)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=color,
                             font=ctk.CTkFont(size=12)).grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            iid = inv.id
            row.bind("<Button-1>", lambda e, i=iid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=iid: self._select(i))

    def _select(self, iid):
        self._selected_id = iid

    def _open_add(self):
        InvoiceFormDialog(self, self._load)

    def _mark_paid(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("mark_paid"), "Please select an invoice.")
            return
        billing_controller.mark_paid(self._selected_id)
        self._load()

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("delete"), "Please select an invoice.")
            return
        if messagebox.askyesno(lang.t("confirm"), lang.t("confirm_delete")):
            billing_controller.delete(self._selected_id)
            self._selected_id = None
            self._load()


class InvoiceFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title(lang.t("create_invoice"))
        self.geometry("520x560")
        self.resizable(False, False)
        self.grab_set()
        self._services = []
        self._build()

    def _build(self):
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=16)
        frame.columnconfigure(0, weight=1)

        patients = patient_controller.get_all()
        doctors = doctor_controller.get_all()
        patient_names = [f"{p.id} — {p.full_name}" for p in patients]
        doctor_names = [f"{d.id} — {d.full_name} (${d.consultation_fee:.0f})" for d in doctors]
        self._patients = patients
        self._doctors = doctors

        def label(text, row):
            ctk.CTkLabel(frame, text=text, anchor="w",
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=12)).grid(row=row, column=0, sticky="w", pady=(8, 0))

        label(lang.t("patient"), 0)
        self.patient_menu = ctk.CTkOptionMenu(frame, values=patient_names or ["—"])
        self.patient_menu.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        label(lang.t("doctor") + " (auto-fills fee)", 2)
        self.doctor_menu = ctk.CTkOptionMenu(frame, values=doctor_names or ["—"],
                                             command=self._on_doctor_change)
        self.doctor_menu.grid(row=3, column=0, sticky="ew", pady=(2, 0))

        label(lang.t("consultation_fee"), 4)
        self.fee_e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                                  text_color=theme.get("entry_fg"),
                                  border_color=theme.get("border"), height=36)
        self.fee_e.insert(0, "0")
        self.fee_e.grid(row=5, column=0, sticky="ew", pady=(2, 0))

        label(lang.t("discount") + " ($)", 6)
        self.discount_e = ctk.CTkEntry(frame, fg_color=theme.get("entry_bg"),
                                       text_color=theme.get("entry_fg"),
                                       border_color=theme.get("border"), height=36)
        self.discount_e.insert(0, "0")
        self.discount_e.grid(row=7, column=0, sticky="ew", pady=(2, 0))

        # Additional services
        label(lang.t("additional_services"), 8)
        svc_frame = ctk.CTkFrame(frame, fg_color=theme.get("table_row_alt"), corner_radius=8)
        svc_frame.grid(row=9, column=0, sticky="ew", pady=(4, 0))

        svc_top = ctk.CTkFrame(svc_frame, fg_color="transparent")
        svc_top.pack(fill="x", padx=8, pady=6)
        self.svc_name_e = ctk.CTkEntry(svc_top, placeholder_text=lang.t("service_name"),
                                       width=180,
                                       fg_color=theme.get("entry_bg"),
                                       text_color=theme.get("entry_fg"))
        self.svc_name_e.pack(side="left", padx=(0, 6))
        self.svc_price_e = ctk.CTkEntry(svc_top, placeholder_text="$",
                                        width=80,
                                        fg_color=theme.get("entry_bg"),
                                        text_color=theme.get("entry_fg"))
        self.svc_price_e.pack(side="left", padx=(0, 6))
        ctk.CTkButton(svc_top, text=lang.t("add_service"), width=100,
                      fg_color=theme.get("accent"),
                      corner_radius=6,
                      command=self._add_service).pack(side="left")
        self.svc_list_frame = ctk.CTkFrame(svc_frame, fg_color="transparent")
        self.svc_list_frame.pack(fill="x", padx=8, pady=(0, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=12)
        ctk.CTkButton(btn_frame, text=lang.t("create_invoice"),
                      fg_color=theme.get("accent"),
                      hover_color=theme.get("accent_hover"),
                      command=self._save).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text=lang.t("cancel"),
                      fg_color=theme.get("border"),
                      text_color=theme.get("text_primary"),
                      hover_color=theme.get("table_row_alt"),
                      command=self.destroy).pack(side="right")

    def _on_doctor_change(self, value):
        try:
            did = int(value.split("—")[0].strip())
            doc = next((d for d in self._doctors if d.id == did), None)
            if doc:
                self.fee_e.delete(0, "end")
                self.fee_e.insert(0, str(doc.consultation_fee))
        except Exception:
            pass

    def _add_service(self):
        name = self.svc_name_e.get().strip()
        try:
            price = float(self.svc_price_e.get().strip() or "0")
        except ValueError:
            price = 0.0
        if not name:
            return
        self._services.append({"name": name, "price": price})
        self.svc_name_e.delete(0, "end")
        self.svc_price_e.delete(0, "end")
        self._refresh_services()

    def _refresh_services(self):
        for w in self.svc_list_frame.winfo_children():
            w.destroy()
        for svc in self._services:
            ctk.CTkLabel(self.svc_list_frame,
                         text=f"• {svc['name']}  ${svc['price']:.2f}",
                         text_color=theme.get("text_primary"),
                         font=ctk.CTkFont(size=12)).pack(anchor="w")

    def _save(self):
        p_str = self.patient_menu.get()
        try:
            pid = int(p_str.split("—")[0].strip())
        except Exception:
            messagebox.showerror(lang.t("error"), lang.t("select_patient"))
            return
        try:
            fee = float(self.fee_e.get().strip() or "0")
            discount = float(self.discount_e.get().strip() or "0")
        except ValueError:
            messagebox.showerror(lang.t("error"), "Fee and discount must be numbers.")
            return
        svc_total = sum(s["price"] for s in self._services)
        total = max(0, fee + svc_total - discount)
        data = {
            "patient_id": pid,
            "invoice_date": datetime.date.today(),
            "consultation_fee": fee,
            "additional_services": self._services,
            "discount": discount,
            "total_amount": total,
            "is_paid": False,
        }
        billing_controller.add(data)
        self.on_save()
        self.destroy()
