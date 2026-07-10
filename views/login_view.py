"""Login screen."""

from tkinter import messagebox

import customtkinter as ctk
from utils import language as lang
from utils import theme
from controllers.auth_controller import login, reset_password


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color="transparent")
        self.on_success = on_success
        self._build()

    def _build(self):
        # Center card
        card = ctk.CTkFrame(self, corner_radius=16, width=420, height=480,
                            fg_color=theme.get("card_bg"))
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Header
        header = ctk.CTkFrame(card, fg_color=theme.get("sidebar_bg"), height=100, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="🏥", font=ctk.CTkFont(size=36)).pack(pady=(14, 0))
        ctk.CTkLabel(header, text=lang.t("app_title"),
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color="#ffffff").pack(pady=(2, 12))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=36, pady=24)

        ctk.CTkLabel(body, text=lang.t("username"),
                     anchor="w", font=ctk.CTkFont(size=13),
                     text_color=theme.get("text_secondary")).pack(fill="x")
        self.username_entry = ctk.CTkEntry(body, height=38, corner_radius=8,
                                           fg_color=theme.get("entry_bg"),
                                           text_color=theme.get("entry_fg"),
                                           border_color=theme.get("border"))
        self.username_entry.pack(fill="x", pady=(2, 12))

        ctk.CTkLabel(body, text=lang.t("password"),
                     anchor="w", font=ctk.CTkFont(size=13),
                     text_color=theme.get("text_secondary")).pack(fill="x")
        self.password_entry = ctk.CTkEntry(body, height=38, show="•", corner_radius=8,
                                           fg_color=theme.get("entry_bg"),
                                           text_color=theme.get("entry_fg"),
                                           border_color=theme.get("border"))
        self.password_entry.pack(fill="x", pady=(2, 20))

        self.error_label = ctk.CTkLabel(body, text="", text_color=theme.get("danger"),
                                        font=ctk.CTkFont(size=12))
        self.error_label.pack()

        btn = ctk.CTkButton(body, text=lang.t("login_button"), height=42,
                            corner_radius=8,
                            fg_color=theme.get("accent"),
                            hover_color=theme.get("accent_hover"),
                            font=ctk.CTkFont(size=14, weight="bold"),
                            command=self._attempt_login)
        btn.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(body, text=lang.t("reset_password"), height=36,
                      corner_radius=8, fg_color="transparent", border_width=1,
                      hover_color=theme.get("card_bg"),
                      command=self._show_reset_password_dialog).pack(fill="x", pady=(8, 0))

        self.username_entry.bind("<Return>", lambda _: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda _: self._attempt_login())
        self.username_entry.focus()

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.error_label.configure(text=lang.t("required_field"))
            return
        user = login(username, password)
        if user:
            self.on_success(user)
        else:
            self.error_label.configure(text=lang.t("invalid_credentials"))
            self.password_entry.delete(0, "end")

    def _show_reset_password_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title(lang.t("reset_password"))
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.geometry("360x320")

        ctk.CTkLabel(dialog, text=lang.t("reset_password"), font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 8))
        ctk.CTkLabel(dialog, text=lang.t("reset_password_hint"), justify="center").pack(padx=20, pady=(0, 12))

        ctk.CTkLabel(dialog, text=lang.t("username"), anchor="w").pack(fill="x", padx=24)
        username_entry = ctk.CTkEntry(dialog, height=38)
        username_entry.insert(0, self.username_entry.get().strip() or "admin")
        username_entry.pack(fill="x", padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text=lang.t("reset_token"), anchor="w").pack(fill="x", padx=24)
        reset_token_entry = ctk.CTkEntry(dialog, height=38)
        reset_token_entry.pack(fill="x", padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text=lang.t("new_password"), anchor="w").pack(fill="x", padx=24)
        new_pw_entry = ctk.CTkEntry(dialog, height=38, show="•")
        new_pw_entry.pack(fill="x", padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text=lang.t("confirm_password"), anchor="w").pack(fill="x", padx=24)
        confirm_pw_entry = ctk.CTkEntry(dialog, height=38, show="•")
        confirm_pw_entry.pack(fill="x", padx=24, pady=(2, 10))

        def submit_reset():
            username = username_entry.get().strip()
            reset_token = reset_token_entry.get().strip()
            new_password = new_pw_entry.get().strip()
            confirm_password = confirm_pw_entry.get().strip()

            if not username or not reset_token or not new_password or not confirm_password:
                messagebox.showerror(lang.t("error"), lang.t("required_field"))
                return
            if new_password != confirm_password:
                messagebox.showerror(lang.t("error"), lang.t("passwords_do_not_match"))
                return

            if reset_password(username, new_password, reset_token):
                messagebox.showinfo(lang.t("success"), lang.t("password_updated"))
                dialog.destroy()
            else:
                messagebox.showerror(lang.t("error"), lang.t("user_not_found"))

        ctk.CTkButton(dialog, text=lang.t("save"), height=40,
                      command=submit_reset).pack(pady=(12, 12))
