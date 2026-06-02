import customtkinter as ctk
import theme as T
from database import authenticate_user


class LoginScreen(ctk.CTkFrame):

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=T.BG_GRAD_TOP)
        self.on_login_success = on_login_success
        self._password_visible = False
        self._anim_step = 0

        # Center layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self._build_card()
        self._start_gradient_anim()

    def _build_card(self):
        self.login_card = ctk.CTkFrame(
            self,
            corner_radius=T.RADIUS_LG,
            fg_color=T.BG_SECONDARY,
            border_width=1,
            border_color=T.BORDER,
            width=400
        )
        self.login_card.grid(row=1, column=1, padx=60, pady=60)
        self.login_card.grid_propagate(False)
        self.login_card.configure(width=400, height=580)

        # ── Logo ─────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        logo_frame.pack(pady=(48, 0))

        # Circular logo badge
        logo_badge = ctk.CTkFrame(
            logo_frame,
            width=72, height=72,
            corner_radius=T.RADIUS_LG,
            fg_color=T.BLUE,
        )
        logo_badge.pack()
        logo_badge.pack_propagate(False)

        ctk.CTkLabel(
            logo_badge,
            text="+",
            font=T.font(36, "bold"),
            text_color=T.TEXT_PRIMARY
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── App Title ─────────────────────────────────────────
        ctk.CTkLabel(
            self.login_card,
            text="MediStock",
            font=T.title_large(),
            text_color=T.TEXT_PRIMARY
        ).pack(pady=(16, 2))

        ctk.CTkLabel(
            self.login_card,
            text="RFID Inventory Control",
            font=T.callout(),
            text_color=T.TEXT_SECONDARY
        ).pack(pady=(0, 32))

        T.separator(self.login_card).pack(fill="x", padx=32, pady=(0, 28))

        # ── Fields ────────────────────────────────────────────
        field_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        field_frame.pack(fill="x", padx=32)

        ctk.CTkLabel(
            field_frame, text="Username",
            font=T.callout_bold(), text_color=T.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))

        self.entry_username = T.text_input(
            field_frame,
            placeholder="Enter your username"
        )
        self.entry_username.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            field_frame, text="Password",
            font=T.callout_bold(), text_color=T.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))

        pw_row = ctk.CTkFrame(field_frame, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, 6))

        self.entry_password = T.text_input(
            pw_row, placeholder="Enter your password",
            show="•"
        )
        self.entry_password.pack(side="left", fill="x", expand=True)

        self.show_pass_btn = ctk.CTkButton(
            pw_row,
            text="Show",
            width=56, height=44,
            corner_radius=T.RADIUS_MD,
            fg_color=T.BG_QUATERNARY,
            hover_color=T.BG_HOVER,
            text_color=T.TEXT_SECONDARY,
            font=T.callout(),
            command=self._toggle_password
        )
        self.show_pass_btn.pack(side="right", padx=(8, 0))

        # ── Error label ───────────────────────────────────────
        self.error_label = ctk.CTkLabel(
            self.login_card, text="",
            font=T.footnote(), text_color=T.RED, height=18
        )
        self.error_label.pack(pady=(10, 0))

        # ── Sign In Button ────────────────────────────────────
        self.login_button = T.primary_button(
            self.login_card,
            text="Sign In",
            height=48,
            command=self._handle_login
        )
        self.login_button.pack(fill="x", padx=32, pady=(8, 0))

        # ── Footer ────────────────────────────────────────────
        ctk.CTkLabel(
            self.login_card,
            text="admin / admin123  ·  staff / staff123",
            font=T.caption(),
            text_color=T.TEXT_TERTIARY
        ).pack(pady=(16, 32))

        # Key bindings
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())
        self.entry_password.bind("<Return>", lambda e: self._handle_login())
        self.entry_username.focus()

    def _start_gradient_anim(self):
        """Subtle animated background by cycling the bg color very slightly."""
        shades = ["#080810", "#0a0a14", "#080810", "#060608"]
        self.configure(fg_color=shades[self._anim_step % len(shades)])
        self._anim_step += 1
        self.after(2000, self._start_gradient_anim)

    def _toggle_password(self):
        if self._password_visible:
            self.entry_password.configure(show="•")
            self.show_pass_btn.configure(text="Show")
            self._password_visible = False
        else:
            self.entry_password.configure(show="")
            self.show_pass_btn.configure(text="Hide")
            self._password_visible = True

    def _handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.error_label.configure(text="Please fill in all fields.")
            return

        self.login_button.configure(
            text="Signing in...",
            state="disabled",
            fg_color=T.BG_QUATERNARY,
            text_color=T.TEXT_SECONDARY
        )
        self.error_label.configure(text="")
        self.after(400, lambda: self._do_auth(username, password))

    def _do_auth(self, username, password):
        user = authenticate_user(username, password)
        if user:
            self.login_button.configure(
                text="✓  Welcome",
                fg_color=T.GREEN,
                text_color=T.TEXT_PRIMARY
            )
            self.after(500, lambda: self.on_login_success(user))
        else:
            self.error_label.configure(text="Incorrect username or password.")
            self.login_button.configure(
                text="Sign In", state="normal",
                fg_color=T.BLUE, text_color=T.TEXT_PRIMARY
            )
            self.entry_password.delete(0, "end")
            self.entry_password.focus()

    def reset(self):
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.error_label.configure(text="")
        self.login_button.configure(
            text="Sign In", state="normal",
            fg_color=T.BLUE, text_color=T.TEXT_PRIMARY
        )
        self.entry_username.focus()
