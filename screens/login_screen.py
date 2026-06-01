import customtkinter as ctk
from database import authenticate_user


class LoginScreen(ctk.CTkFrame):

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.login_card = ctk.CTkFrame(self, corner_radius=16, fg_color="#1a1a2e",
                                       border_width=1, border_color="#2b2b4a")
        self.login_card.grid(row=1, column=1, padx=40, pady=40)

        self.logo_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        self.logo_frame.pack(pady=(40, 5), padx=60)

        self.logo_icon = ctk.CTkLabel(
            self.logo_frame,
            text="🏥",
            font=ctk.CTkFont(size=48)
        )
        self.logo_icon.pack()

        self.app_title = ctk.CTkLabel(
            self.login_card,
            text="RFID Stock Management",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color="#e0e0ff"
        )
        self.app_title.pack(pady=(5, 0))

        self.app_subtitle = ctk.CTkLabel(
            self.login_card,
            text="Healthcare Inventory Control System",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="#7a7a9e"
        )
        self.app_subtitle.pack(pady=(2, 25))

        self.divider = ctk.CTkFrame(self.login_card, height=1, fg_color="#2b2b4a")
        self.divider.pack(fill="x", padx=30, pady=(0, 25))

        self.user_label = ctk.CTkLabel(
            self.login_card,
            text="👤  Username",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a0a0c0",
            anchor="w"
        )
        self.user_label.pack(padx=40, anchor="w")

        self.entry_username = ctk.CTkEntry(
            self.login_card,
            placeholder_text="Enter your username",
            width=300,
            height=42,
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            border_color="#2b2b4a",
            fg_color="#16162a"
        )
        self.entry_username.pack(padx=40, pady=(5, 15))

        self.pass_label = ctk.CTkLabel(
            self.login_card,
            text="🔒  Password",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#a0a0c0",
            anchor="w"
        )
        self.pass_label.pack(padx=40, anchor="w")

        self.password_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        self.password_frame.pack(padx=40, pady=(5, 5), fill="x")

        self.entry_password = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="Enter your password",
            show="•",
            height=42,
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            border_color="#2b2b4a",
            fg_color="#16162a"
        )
        self.entry_password.pack(side="left", fill="x", expand=True)

        self.show_pass_btn = ctk.CTkButton(
            self.password_frame,
            text="👁",
            width=42,
            height=42,
            corner_radius=8,
            fg_color="#2b2b4a",
            hover_color="#3b3b5a",
            command=self._toggle_password
        )
        self.show_pass_btn.pack(side="right", padx=(8, 0))

        self._password_visible = False

        self.error_label = ctk.CTkLabel(
            self.login_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#e74c3c",
            height=20
        )
        self.error_label.pack(pady=(5, 0))

        self.login_button = ctk.CTkButton(
            self.login_card,
            text="Sign In",
            width=300,
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8,
            fg_color="#2b719e",
            hover_color="#1f538d",
            command=self._handle_login
        )
        self.login_button.pack(padx=40, pady=(10, 15))

        self.role_info = ctk.CTkLabel(
            self.login_card,
            text="Demo: admin/admin123 or staff/staff123",
            font=ctk.CTkFont(size=11),
            text_color="#555577"
        )
        self.role_info.pack(pady=(0, 10))

        self.footer = ctk.CTkLabel(
            self.login_card,
            text="© 2025 RFID Stock Management System  •  v2.0",
            font=ctk.CTkFont(size=10),
            text_color="#44445e"
        )
        self.footer.pack(pady=(5, 25))

        self.entry_password.bind("<Return>", lambda e: self._handle_login())
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())

    def _toggle_password(self):
        if self._password_visible:
            self.entry_password.configure(show="•")
            self.show_pass_btn.configure(text="👁")
            self._password_visible = False
        else:
            self.entry_password.configure(show="")
            self.show_pass_btn.configure(text="🔒")
            self._password_visible = True

    def _handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.error_label.configure(text="⚠ Please fill in all fields")
            return

        self.login_button.configure(text="Authenticating...", state="disabled")
        self.error_label.configure(text="")

        self.after(500, lambda: self._do_auth(username, password))

    def _do_auth(self, username, password):
        user = authenticate_user(username, password)

        if user:
            user_id, uname, role, full_name = user
            self.login_button.configure(text="✓ Success!", fg_color="#2ecc71")
            self.after(600, lambda: self.on_login_success(user))
        else:
            self.error_label.configure(text="✖ Invalid username or password")
            self.login_button.configure(text="Sign In", state="normal")
            self.entry_password.delete(0, "end")
            self.entry_password.focus()

    def reset(self):
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.error_label.configure(text="")
        self.login_button.configure(text="Sign In", state="normal", fg_color="#2b719e")
        self.entry_username.focus()
