"""Billing / Invoice view."""

import json
import datetime
import os
import webbrowser
from html import escape
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox
from utils import language as lang
from utils import theme
from controllers import billing_controller, patient_controller, doctor_controller


class BillingView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._selected_id = None
        self._row_frames = {}
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
            (lang.t("print"), self._print_selected, theme.get("accent")),
            (lang.t("mark_paid"), self._mark_paid, theme.get("success")),
            (lang.t("delete"), self._delete, theme.get("danger")),
        ]:
            ctk.CTkButton(top, text=label, width=110, fg_color=color,
                          hover_color=theme.get("accent_hover"),
                          corner_radius=8, command=cmd).pack(side="right", padx=4)

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        headers = ["#", lang.t("patient"), lang.t("invoice_number"),
                   lang.t("doctor"), lang.t("visit_date"), lang.t("total_amount"), lang.t("payment_status")]
        widths = [40, 160, 90, 140, 110, 110, 100]

        hf = ctk.CTkFrame(card, fg_color=theme.get("table_header"), corner_radius=0)
        hf.pack(fill="x")
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=theme.get("text_primary"),
                         anchor="e" if lang.is_rtl() else "w",
                         justify="right" if lang.is_rtl() else "left").grid(row=0, column=i, padx=8, pady=8, sticky="w")

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self._widths = widths

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._row_frames.clear()
        try:
            invoices = billing_controller.get_all()
        except Exception as e:
            messagebox.showerror(lang.t("error"), f"Failed to load invoices: {str(e)}")
            return
        
        if not invoices:
            ctk.CTkLabel(self.scroll, text=lang.t("no_records"),
                         text_color=theme.get("text_secondary")).pack(pady=20)
            return
        
        for idx, inv_data in enumerate(invoices):
            bg = theme.get("card_bg") if idx % 2 == 0 else theme.get("table_row_alt")
            row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            paid_text = lang.t("paid") if inv_data['is_paid'] else lang.t("unpaid")
            paid_color = theme.get("success") if inv_data['is_paid'] else theme.get("danger")
            
            vals = [
                str(idx + 1),
                inv_data['patient_name'],
                f"INV-{inv_data['id']:04d}",
                inv_data.get('doctor_name') or '—',
                str(inv_data['invoice_date']),
                f"${inv_data['total_amount']:.2f}",
                paid_text,
            ]
            colors_list = [
                theme.get("text_primary")] * 6 + [paid_color]
            for ci, (val, w, color) in enumerate(zip(vals, self._widths, colors_list)):
                ctk.CTkLabel(row, text=val, width=w,
                             text_color=color,
                             font=ctk.CTkFont(size=13),
                             anchor="e" if lang.is_rtl() else "w",
                             justify="right" if lang.is_rtl() else "left").grid(row=0, column=ci, padx=8, pady=0, sticky="w")
            self._row_frames[inv_data['id']] = (row, bg)
            iid = inv_data['id']
            row.bind("<Button-1>", lambda e, i=iid: self._select(i))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, i=iid: self._select(i))

    def _select(self, iid):
        if self._selected_id and self._selected_id in self._row_frames:
            prev_row, prev_bg = self._row_frames[self._selected_id]
            try: prev_row.configure(fg_color=prev_bg)
            except Exception: pass
        self._selected_id = iid
        if iid in self._row_frames:
            row, _ = self._row_frames[iid]
            try: row.configure(fg_color="#1976d2")
            except Exception: pass

    def _open_add(self):
        try:
            InvoiceFormDialog(self, self._load)
        except Exception as e:
            messagebox.showerror(lang.t("error"), f"Failed to open invoice form: {str(e)}")

    def _mark_paid(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("mark_paid"), "Please select an invoice.")
            return
        if not messagebox.askyesno(lang.t("confirm"), lang.t("confirm_mark_paid")):
            return
        billing_controller.mark_paid(self._selected_id)
        self._load()

    def _print_selected(self):
        if not self._selected_id:
            messagebox.showinfo(lang.t("print"), "Please select an invoice.")
            return
        invoices = billing_controller.get_all()
        invoice = next((inv for inv in invoices if inv['id'] == self._selected_id), None)
        if not invoice:
            messagebox.showerror(lang.t("error"), "Invoice not found.")
            return

        output_dir = Path(__file__).resolve().parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        html_path = output_dir / f"invoice_{invoice['id']}.html"
        html_path.write_text(self._render_invoice_html(invoice), encoding="utf-8")

        try:
            if hasattr(os, "startfile"):
                os.startfile(str(html_path))
            else:
                webbrowser.open_new_tab(html_path.as_uri())
            messagebox.showinfo(lang.t("success"), lang.t("invoice_printed"))
        except Exception as exc:
            messagebox.showerror(lang.t("error"), f"Failed to open invoice for printing: {exc}")

    def _render_invoice_html(self, invoice):
        services = invoice.get("additional_services") or []
        if isinstance(services, str):
            try:
                services = json.loads(services)
            except Exception:
                services = []

        service_rows = "".join(
            f"<tr><td>{escape(str(s.get('name', '')))}</td><td>{s.get('price', 0):.2f}</td></tr>"
            for s in services
        )
        rtl = "rtl" if lang.is_rtl() else "ltr"
        return f"""<!DOCTYPE html>
<html dir=\"{rtl}\" lang=\"{lang.current()}\">
<head>
  <meta charset=\"utf-8\" />
  <title>Invoice {invoice['id']}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    .title {{ font-size: 24px; font-weight: bold; margin-bottom: 12px; }}
    .meta {{ margin-bottom: 12px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f3f3f3; }}
    .total {{ font-weight: bold; margin-top: 12px; }}
  </style>
</head>
<body>
  <div class=\"title\">{escape(lang.t('billing'))}</div>
  <div class=\"meta\">{escape(lang.t('invoice_number'))}: INV-{invoice['id']:04d}</div>
  <div class=\"meta\">{escape(lang.t('patient'))}: {escape(invoice.get('patient_name') or '—')}</div>
  <div class=\"meta\">{escape(lang.t('doctor'))}: {escape(invoice.get('doctor_name') or '—')}</div>
  <div class=\"meta\">{escape(lang.t('visit_date'))}: {invoice['invoice_date']}</div>
  <div class=\"meta\">{escape(lang.t('consultation_fee'))}: ${invoice.get('consultation_fee', 0):.2f}</div>
  <div class=\"meta\">{escape(lang.t('discount'))}: ${invoice.get('discount', 0):.2f}</div>
  <table>
    <thead><tr><th>{escape(lang.t('service_name'))}</th><th>{escape(lang.t('service_price'))}</th></tr></thead>
    <tbody>{service_rows}</tbody>
  </table>
  <div class=\"total\">{escape(lang.t('total_amount'))}: ${invoice.get('total_amount', 0):.2f}</div>
</body>
</html>"""

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
        self.geometry("540x600")
        self.minsize(500, 540)
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
                         font=ctk.CTkFont(size=13)).grid(row=row, column=0, sticky="w", pady=(8, 0))

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

        doctor_id = None
        try:
            doctor_text = self.doctor_menu.get()
            doctor_id = int(doctor_text.split("—")[0].strip()) if doctor_text else None
        except Exception:
            doctor_id = None
        
        svc_total = sum(s["price"] for s in self._services)
        total = max(0, fee + svc_total - discount)
        data = {
            "patient_id": pid,
            "doctor_id": doctor_id,
            "invoice_date": datetime.date.today(),
            "consultation_fee": fee,
            "additional_services": self._services,
            "discount": discount,
            "total_amount": total,
            "is_paid": False,
        }
        try:
            result = billing_controller.add(data)
            if result and result.id:
                messagebox.showinfo(lang.t("success"), lang.t("invoice_created"))
                self.on_save()
                self.destroy()
            else:
                messagebox.showerror(lang.t("error"), "Failed to create invoice.")
        except Exception as e:
            messagebox.showerror(lang.t("error"), f"Error creating invoice: {str(e)}")
