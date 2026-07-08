"""Settings view — clinic info, theme, language."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils import language as lang
from utils import theme
from controllers import settings_controller, auth_controller


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self._settings = settings_controller.get()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=lang.t("settings"),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=theme.get("text_primary")).pack(anchor="w", padx=28, pady=(24, 16))

        card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        card.pack(fill="x", padx=28, pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=32, pady=24, fill="x")
        inner.columnconfigure(1, weight=1)

        s = self._settings

        def row(label, row_idx, widget):
            ctk.CTkLabel(inner, text=label,
                         anchor="w", width=160,
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=13)).grid(row=row_idx, column=0, sticky="w", pady=8)
            widget.grid(row=row_idx, column=1, sticky="ew", padx=(12, 0))
            return widget

        # Clinic name
        self.name_e = ctk.CTkEntry(inner, fg_color=theme.get("entry_bg"),
                                   text_color=theme.get("entry_fg"),
                                   border_color=theme.get("border"), height=38)
        self.name_e.insert(0, s.clinic_name if s else "My Clinic")
        row(lang.t("clinic_name"), 0, self.name_e)

        # Logo
        logo_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self.logo_label = ctk.CTkLabel(logo_frame, text=s.logo_path if s and s.logo_path else "No logo selected",
                                       text_color=theme.get("text_secondary"),
                                       font=ctk.CTkFont(size=11))
        self.logo_label.pack(side="left", expand=True, fill="x")
        ctk.CTkButton(logo_frame, text=lang.t("change_logo"), width=120,
                      fg_color=theme.get("accent"),
                      corner_radius=6,
                      command=self._pick_logo).pack(side="right")
        self._logo_path = s.logo_path if s else ""
        row(lang.t("clinic_logo"), 1, logo_frame)

        # Theme
        self.theme_var = ctk.StringVar(value=s.theme if s else "light")
        theme_frame = ctk.CTkFrame(inner, fg_color="transparent")
        ctk.CTkRadioButton(theme_frame, text=lang.t("light"),
                           variable=self.theme_var, value="light").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(theme_frame, text=lang.t("dark"),
                           variable=self.theme_var, value="dark").pack(side="left")
        row(lang.t("theme"), 2, theme_frame)

        # Language
        self.lang_var = ctk.StringVar(value=s.language if s else "en")
        lang_frame = ctk.CTkFrame(inner, fg_color="transparent")
        ctk.CTkRadioButton(lang_frame, text=lang.t("english"),
                           variable=self.lang_var, value="en").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(lang_frame, text=lang.t("arabic"),
                           variable=self.lang_var, value="ar").pack(side="left")
        row(lang.t("language"), 3, lang_frame)

        # Save button
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=32, pady=(0, 24))
        ctk.CTkButton(btn_frame, text=lang.t("save_settings"),
                      height=40,
                      fg_color=theme.get("accent"),
                      hover_color=theme.get("accent_hover"),
                      corner_radius=8,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save).pack(side="right")

        # Change password section
        pw_card = ctk.CTkFrame(self, fg_color=theme.get("card_bg"), corner_radius=12)
        pw_card.pack(fill="x", padx=28, pady=(0, 16))

        inner_pw = ctk.CTkFrame(pw_card, fg_color="transparent")
        inner_pw.pack(padx=32, pady=16, fill="x")
        inner_pw.columnconfigure(1, weight=1)

        def pw_row(label, row_idx, widget):
            ctk.CTkLabel(inner_pw, text=label,
                         anchor="w", width=160,
                         text_color=theme.get("text_secondary"),
                         font=ctk.CTkFont(size=13)).grid(row=row_idx, column=0, sticky="w", pady=8)
            widget.grid(row=row_idx, column=1, sticky="ew", padx=(12, 0))
            return widget

        self.current_pw = ctk.CTkEntry(inner_pw, show="•", fg_color=theme.get("entry_bg"), height=36)
        pw_row(lang.t("current_password") if lang.t("current_password") != "current_password" else "Current password", 0, self.current_pw)

        self.new_pw = ctk.CTkEntry(inner_pw, show="•", fg_color=theme.get("entry_bg"), height=36)
        pw_row(lang.t("new_password") if lang.t("new_password") != "new_password" else "New password", 1, self.new_pw)

        self.confirm_pw = ctk.CTkEntry(inner_pw, show="•", fg_color=theme.get("entry_bg"), height=36)
        pw_row(lang.t("confirm_password") if lang.t("confirm_password") != "confirm_password" else "Confirm password", 2, self.confirm_pw)

        ctk.CTkButton(inner_pw, text=lang.t("change_password") if lang.t("change_password") != "change_password" else "Change password",
                      height=36, fg_color=theme.get("accent"), hover_color=theme.get("accent_hover"),
                      corner_radius=8, command=self._change_password).grid(row=3, column=1, sticky="e", pady=(8, 0))

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            self._logo_path = path
            self.logo_label.configure(text=path)

    def _change_password(self):
        cur = self.current_pw.get().strip()
        new = self.new_pw.get().strip()
        conf = self.confirm_pw.get().strip()
        if not cur or not new:
            messagebox.showerror(lang.t("error"), "Please fill all password fields.")
            return
        if new != conf:
            messagebox.showerror(lang.t("error"), "New password and confirmation do not match.")
            return
        try:
            ok = auth_controller.change_password(self.user.id, cur, new)
        except Exception as e:
            messagebox.showerror(lang.t("error"), str(e))
            return
        if not ok:
            messagebox.showerror(lang.t("error"), "Current password is incorrect.")
            return
        # Success
        self.current_pw.delete(0, "end")
        self.new_pw.delete(0, "end")
        self.confirm_pw.delete(0, "end")
        messagebox.showinfo(lang.t("success"), "Password changed successfully.")

    def _save(self):
        data = {
            "clinic_name": self.name_e.get().strip() or "My Clinic",
            "theme": self.theme_var.get(),
            "language": self.lang_var.get(),
            "logo_path": self._logo_path,
        }
        settings_controller.save(data)
        messagebox.showinfo(lang.t("success"), lang.t("settings_saved") + "\n" + lang.t("restart_required"))
