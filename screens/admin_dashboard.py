import customtkinter as ctk
import theme as T
from database import (get_all_users, get_system_settings, update_system_setting,
                      get_inventory_stats, get_all_movements,
                      add_user, delete_user, update_user_password)


class AdminDashboard(ctk.CTkFrame):

    def __init__(self, parent, on_logout, current_user=None):
        super().__init__(parent, fg_color=T.BG_PRIMARY)
        self.on_logout = on_logout
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(3, weight=2)
        self._build_navbar()
        self._build_stats()
        self._build_content()
        self._build_logs()

    # ─── Navbar ───────────────────────────────────────────────────────────────
    def _build_navbar(self):
        nav = T.navbar(self)
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            nav, text="Administrator",
            font=T.headline(), text_color=T.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=16, sticky="w")

        name = self.current_user[3] if self.current_user else "Admin"
        ctk.CTkLabel(
            nav, text=name,
            font=T.callout(), text_color=T.TEXT_SECONDARY
        ).grid(row=0, column=1, sticky="e", padx=12)

        T.danger_button(
            nav, text="Sign Out", width=90, height=32,
            command=self.on_logout
        ).grid(row=0, column=2, padx=16, pady=12)

    # ─── Stat Cards ───────────────────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)

        stats = get_inventory_stats()
        data = [
            ("Total Products",    str(stats["total_products"]),  T.BLUE),
            ("Active RFID Tags",  str(stats["total_rfid"]),      T.PURPLE),
            ("Low Stock Alerts",  str(stats["low_stock_alerts"]), T.ORANGE),
            ("Expired Items",     str(stats["expired_items"]),    T.RED),
        ]
        for i, (label_text, value, color) in enumerate(data):
            card = ctk.CTkFrame(
                sf, corner_radius=T.RADIUS_MD,
                fg_color=T.BG_SECONDARY,
                border_width=0
            )
            card.grid(row=0, column=i, padx=5, sticky="ew", ipady=4)

            # Colored left accent bar
            accent = ctk.CTkFrame(card, width=4, corner_radius=2, fg_color=color)
            accent.pack(side="left", fill="y", padx=(12, 0), pady=12)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)

            ctk.CTkLabel(
                inner, text=value,
                font=T.font(30, "bold"), text_color=color
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=label_text,
                font=T.caption(), text_color=T.TEXT_SECONDARY
            ).pack(anchor="w")

    # ─── Main Content (Users + Settings) ──────────────────────────────────────
    def _build_content(self):
        cf = ctk.CTkFrame(self, fg_color="transparent")
        cf.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        cf.grid_columnconfigure(0, weight=3)
        cf.grid_columnconfigure(1, weight=2)
        cf.grid_rowconfigure(0, weight=1)
        self._build_users_panel(cf)
        self._build_settings_panel(cf)

    def _build_users_panel(self, parent):
        self.users_card = T.card(parent)
        self.users_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.users_card.grid_rowconfigure(2, weight=1)
        self.users_card.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(self.users_card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            hdr, text="User Management",
            font=T.subheadline(), text_color=T.TEXT_PRIMARY
        ).pack(side="left")
        T.primary_button(
            hdr, text="+ Add User", width=100, height=30,
            command=self._open_add_user_dialog
        ).pack(side="right")

        # Table header
        th = ctk.CTkFrame(self.users_card, fg_color=T.BG_TERTIARY, corner_radius=T.RADIUS_SM)
        th.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
        for text, w in [("ID", 40), ("Username", 110), ("Full Name", 150), ("Role", 80), ("Actions", 120)]:
            ctk.CTkLabel(
                th, text=text, width=w,
                font=T.caption(), text_color=T.TEXT_SECONDARY
            ).pack(side="left", padx=6, pady=8)

        self.users_list = ctk.CTkScrollableFrame(self.users_card, fg_color="transparent")
        self.users_list.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self._populate_users()

    def _populate_users(self):
        for w in self.users_list.winfo_children():
            w.destroy()
        current_uid = self.current_user[0] if self.current_user else None

        for idx, (uid, uname, role, full_name) in enumerate(get_all_users()):
            bg = T.BG_SECONDARY if idx % 2 == 0 else T.BG_TERTIARY
            row = ctk.CTkFrame(self.users_list, fg_color=bg, corner_radius=T.RADIUS_SM, height=44)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(uid), width=40,
                         font=T.caption(), text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=uname, width=110,
                         font=T.callout_bold(), text_color=T.TEXT_PRIMARY
                         ).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=full_name, width=150,
                         font=T.callout(), text_color=T.TEXT_PRIMARY
                         ).pack(side="left", padx=4)

            r_color = T.PURPLE if role == "admin" else T.BLUE
            r_text  = "Admin" if role == "admin" else "Staff"
            role_badge = ctk.CTkFrame(row, fg_color=r_color, corner_radius=T.RADIUS_SM, width=56, height=22)
            role_badge.pack(side="left", padx=8)
            role_badge.pack_propagate(False)
            ctk.CTkLabel(
                role_badge, text=r_text, font=T.caption(), text_color=T.TEXT_PRIMARY
            ).place(relx=0.5, rely=0.5, anchor="center")

            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.pack(side="left", padx=4)

            ctk.CTkButton(
                bf, text="Password", width=72, height=26,
                corner_radius=T.RADIUS_SM,
                fg_color=T.BG_QUATERNARY, hover_color=T.PURPLE,
                text_color=T.TEXT_SECONDARY, font=T.caption(),
                command=lambda u=uid, n=uname: self._open_change_password_dialog(u, n)
            ).pack(side="left", padx=(0, 4))

            is_self = (uid == current_uid)
            ctk.CTkButton(
                bf, text="Delete", width=56, height=26,
                corner_radius=T.RADIUS_SM,
                fg_color=T.BG_QUATERNARY if not is_self else T.BG_TERTIARY,
                hover_color=T.RED if not is_self else T.BG_TERTIARY,
                text_color=T.TEXT_SECONDARY, font=T.caption(),
                state="normal" if not is_self else "disabled",
                command=lambda u=uid, n=uname: self._confirm_delete_user(u, n)
            ).pack(side="left")

    # ─── Add User Dialog ──────────────────────────────────────────────────────
    def _open_add_user_dialog(self):
        d = self._dialog("Add User", 420, 500)

        ctk.CTkLabel(d, text="Add New User",
                     font=T.headline(), text_color=T.TEXT_PRIMARY
                     ).pack(pady=(28, 4))
        T.separator(d).pack(fill="x", padx=28, pady=(4, 20))

        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=28)

        full_name_entry = self._field(form, "Full Name", "e.g. Dr. Ahmet Yilmaz")
        username_entry  = self._field(form, "Username",  "e.g. ahmet")
        password_entry  = self._field(form, "Password",  "Min. 6 characters", show="•")

        ctk.CTkLabel(form, text="Role", font=T.callout_bold(),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 6))
        role_var = ctk.StringVar(value="staff")
        role_seg = ctk.CTkSegmentedButton(
            form, values=["staff", "admin"], variable=role_var,
            selected_color=T.BLUE, selected_hover_color=T.BLUE_HOVER,
            unselected_color=T.BG_QUATERNARY, unselected_hover_color=T.BG_HOVER,
            font=T.callout_bold()
        )
        role_seg.pack(fill="x", pady=(0, 8))

        feedback = ctk.CTkLabel(form, text="", font=T.footnote(), text_color=T.RED)
        feedback.pack(pady=(4, 0))

        def _save():
            fn = full_name_entry.get().strip()
            un = username_entry.get().strip()
            pw = password_entry.get().strip()
            rl = role_var.get()
            if not fn or not un or not pw:
                feedback.configure(text="All fields are required.")
                return
            if len(pw) < 6:
                feedback.configure(text="Password must be at least 6 characters.")
                return
            if not add_user(un, pw, rl, fn):
                feedback.configure(text=f"Username '{un}' already exists.")
                return
            feedback.configure(text="User created.", text_color=T.GREEN)
            self._populate_users()
            d.after(1000, d.destroy)

        T.primary_button(d, text="Create User", height=44, command=_save
                         ).pack(fill="x", padx=28, pady=(16, 8))
        T.secondary_button(d, text="Cancel", height=36, command=d.destroy
                           ).pack(fill="x", padx=28)

    # ─── Change Password Dialog ───────────────────────────────────────────────
    def _open_change_password_dialog(self, user_id, username):
        d = self._dialog("Change Password", 380, 300)

        ctk.CTkLabel(d, text="Change Password",
                     font=T.headline(), text_color=T.TEXT_PRIMARY
                     ).pack(pady=(28, 4))
        ctk.CTkLabel(d, text=f"User: {username}",
                     font=T.callout(), text_color=T.TEXT_SECONDARY
                     ).pack(pady=(0, 16))

        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=28)

        pw_entry = self._field(form, "New Password", "Min. 6 characters", show="•")
        pw_conf  = self._field(form, "Confirm Password", "Repeat password", show="•")

        feedback = ctk.CTkLabel(form, text="", font=T.footnote())
        feedback.pack(pady=(4, 0))

        def _save():
            pw  = pw_entry.get().strip()
            pw2 = pw_conf.get().strip()
            if len(pw) < 6:
                feedback.configure(text="Min. 6 characters required.", text_color=T.RED)
                return
            if pw != pw2:
                feedback.configure(text="Passwords do not match.", text_color=T.RED)
                return
            update_user_password(user_id, pw)
            feedback.configure(text="Password updated.", text_color=T.GREEN)
            d.after(1000, d.destroy)

        T.primary_button(d, text="Update Password", height=42, command=_save,
                         fg_color=T.PURPLE, hover_color=T.PURPLE_HOVER
                         ).pack(fill="x", padx=28, pady=(16, 8))
        T.secondary_button(d, text="Cancel", height=36, command=d.destroy
                           ).pack(fill="x", padx=28)

    # ─── Delete User Dialog ───────────────────────────────────────────────────
    def _confirm_delete_user(self, user_id, username):
        d = self._dialog("Delete User", 360, 210)

        ctk.CTkLabel(d, text="Delete User",
                     font=T.headline(), text_color=T.RED
                     ).pack(pady=(28, 8))
        ctk.CTkLabel(
            d,
            text=f'Remove "{username}"?\nThis action cannot be undone.',
            font=T.callout(), text_color=T.TEXT_SECONDARY, justify="center"
        ).pack(pady=(0, 24))

        btns = ctk.CTkFrame(d, fg_color="transparent")
        btns.pack(fill="x", padx=28)

        def _delete():
            delete_user(user_id)
            self._populate_users()
            d.destroy()

        T.secondary_button(btns, text="Cancel", width=130, height=40,
                           command=d.destroy).pack(side="left", padx=(0, 8))
        T.danger_button(btns, text="Delete", width=130, height=40,
                        command=_delete).pack(side="left")

    # ─── Settings Panel ───────────────────────────────────────────────────────
    def _build_settings_panel(self, parent):
        card = T.card(parent)
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(card, text="System Settings",
                     font=T.subheadline(), text_color=T.TEXT_PRIMARY
                     ).pack(pady=(20, 16), padx=20, anchor="w")

        settings = get_system_settings()

        # Low stock threshold
        ctk.CTkLabel(card, text="Low Stock Threshold",
                     font=T.callout_bold(), text_color=T.TEXT_SECONDARY
                     ).pack(padx=20, anchor="w")

        tf = ctk.CTkFrame(card, fg_color="transparent")
        tf.pack(fill="x", padx=20, pady=(6, 16))
        self.threshold_slider = ctk.CTkSlider(
            tf, from_=5, to=100, number_of_steps=19,
            button_color=T.BLUE, button_hover_color=T.BLUE_HOVER,
            progress_color=T.BLUE, command=self._upd_thr
        )
        self.threshold_slider.set(int(settings.get("low_stock_threshold", "20")))
        self.threshold_slider.pack(side="left", fill="x", expand=True)
        self.thr_label = ctk.CTkLabel(
            tf, text=f"{settings.get('low_stock_threshold','20')} units",
            font=T.callout_bold(), text_color=T.TEXT_PRIMARY, width=72
        )
        self.thr_label.pack(side="right", padx=(10, 0))

        # Expiry warning period
        ctk.CTkLabel(card, text="Expiry Warning Period",
                     font=T.callout_bold(), text_color=T.TEXT_SECONDARY
                     ).pack(padx=20, anchor="w", pady=(8, 0))

        ef = ctk.CTkFrame(card, fg_color="transparent")
        ef.pack(fill="x", padx=20, pady=(6, 16))
        self.expiry_slider = ctk.CTkSlider(
            ef, from_=30, to=365, number_of_steps=11,
            button_color=T.ORANGE, button_hover_color=T.ORANGE_HOVER,
            progress_color=T.ORANGE, command=self._upd_exp
        )
        self.expiry_slider.set(int(settings.get("expiry_warning_days", "90")))
        self.expiry_slider.pack(side="left", fill="x", expand=True)
        self.exp_label = ctk.CTkLabel(
            ef, text=f"{settings.get('expiry_warning_days','90')} days",
            font=T.callout_bold(), text_color=T.TEXT_PRIMARY, width=72
        )
        self.exp_label.pack(side="right", padx=(10, 0))

        T.separator(card).pack(fill="x", padx=20, pady=8)

        self.save_btn = T.primary_button(
            card, text="Save Settings", height=40,
            command=self._save
        )
        self.save_btn.pack(fill="x", padx=20, pady=(4, 20))

    # ─── Transaction Logs ─────────────────────────────────────────────────────
    def _build_logs(self):
        card = T.card(self)
        card.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        ctk.CTkLabel(
            hdr, text="Transaction Logs",
            font=T.subheadline(), text_color=T.TEXT_PRIMARY
        ).pack(side="left")
        T.secondary_button(
            hdr, text="Refresh", width=80, height=28,
            command=self._refresh_logs
        ).pack(side="right")

        th = ctk.CTkFrame(card, fg_color=T.BG_TERTIARY, corner_radius=T.RADIUS_SM)
        th.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
        for text, w in [("#", 35), ("Date & Time", 160), ("Staff", 150),
                        ("Medicine", 120), ("RFID Tag", 110), ("Action", 100)]:
            ctk.CTkLabel(
                th, text=text, width=w,
                font=T.caption(), text_color=T.TEXT_SECONDARY
            ).pack(side="left", padx=6, pady=8)

        self.logs_body = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.logs_body.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self._populate_logs()

    def _populate_logs(self):
        for w in self.logs_body.winfo_children():
            w.destroy()

        movements = get_all_movements()
        if not movements:
            ctk.CTkLabel(
                self.logs_body,
                text="No transactions recorded yet.",
                font=T.callout(), text_color=T.TEXT_TERTIARY
            ).pack(pady=20)
            return

        for idx, (mid, rfid_tag, product_name, action, user_name, date) in enumerate(movements, 1):
            bg = T.BG_SECONDARY if idx % 2 == 1 else T.BG_TERTIARY
            row = ctk.CTkFrame(self.logs_body, fg_color=bg, corner_radius=T.RADIUS_SM, height=36)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(idx), width=35,
                         font=T.caption(), text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=date or "-", width=160,
                         font=ctk.CTkFont(family="SF Mono", size=11),
                         text_color=T.TEAL
                         ).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=user_name or "Unknown", width=150,
                         font=T.callout_bold(), text_color=T.TEXT_PRIMARY
                         ).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=product_name or "-", width=120,
                         font=T.callout(), text_color=T.TEXT_PRIMARY
                         ).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rfid_tag or "-", width=110,
                         font=ctk.CTkFont(family="SF Mono", size=11),
                         text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=6)

            if action == "DISPENSED":
                a_color, a_text = T.ORANGE, "Dispensed"
            elif action == "RETURNED":
                a_color, a_text = T.GREEN, "Returned"
            elif action == "ADDED":
                a_color, a_text = T.BLUE, "Added"
            else:
                a_color, a_text = T.TEXT_SECONDARY, action

            # Action pill badge
            badge = ctk.CTkFrame(row, fg_color=a_color, corner_radius=T.RADIUS_SM, width=72, height=22)
            badge.pack(side="left", padx=8)
            badge.pack_propagate(False)
            ctk.CTkLabel(
                badge, text=a_text, font=T.caption(), text_color=T.TEXT_PRIMARY
            ).place(relx=0.5, rely=0.5, anchor="center")

    # ─── Helpers ──────────────────────────────────────────────────────────────
    def _refresh_logs(self):
        self._populate_logs()

    def _upd_thr(self, v):
        self.thr_label.configure(text=f"{int(v)} units")

    def _upd_exp(self, v):
        self.exp_label.configure(text=f"{int(v)} days")

    def _save(self):
        update_system_setting("low_stock_threshold", int(self.threshold_slider.get()))
        update_system_setting("expiry_warning_days", int(self.expiry_slider.get()))
        self.save_btn.configure(text="Saved", fg_color=T.GREEN)
        self.after(2000, lambda: self.save_btn.configure(text="Save Settings", fg_color=T.BLUE))

    def _dialog(self, title, w, h):
        d = ctk.CTkToplevel(self)
        d.title(title)
        d.geometry(f"{w}x{h}")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=T.BG_SECONDARY)
        d.lift()
        d.focus_force()
        return d

    def _field(self, parent, label_text, placeholder="", show=""):
        ctk.CTkLabel(parent, text=label_text, font=T.callout_bold(),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        e = T.text_input(parent, placeholder=placeholder, height=40)
        if show:
            e.configure(show=show)
        e.pack(fill="x", pady=(0, 12))
        return e
