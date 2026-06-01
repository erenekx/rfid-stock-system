import customtkinter as ctk
from database import (get_all_users, get_system_settings, update_system_setting,
                      get_inventory_stats, get_all_movements,
                      add_user, delete_user, update_user_password)


class AdminDashboard(ctk.CTkFrame):

    def __init__(self, parent, on_logout, current_user=None):
        super().__init__(parent, fg_color="transparent")
        self.on_logout = on_logout
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(3, weight=2)
        self._build_navbar()
        self._build_stats()
        self._build_content()
        self._build_logs()

    def _build_navbar(self):
        self.navbar = ctk.CTkFrame(self, height=50, corner_radius=10, fg_color="#1a1a2e",
                                   border_width=1, border_color="#2b2b4a")
        self.navbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.navbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.navbar, text="🛡️  Administrator Dashboard",
                     font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
                     text_color="#e0e0ff").grid(row=0, column=0, padx=20, pady=12, sticky="w")

        name = self.current_user[3] if self.current_user else "Admin"
        ctk.CTkLabel(self.navbar, text=f"👤 {name}", font=ctk.CTkFont(size=13),
                     text_color="#7a7a9e").grid(row=0, column=1, sticky="e", padx=5)

        ctk.CTkButton(self.navbar, text="⏻ Logout", width=100, height=34, corner_radius=8,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.on_logout).grid(row=0, column=2, padx=15, pady=10)

    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)
        stats = get_inventory_stats()
        data = [
            ("📦", "Total Products", str(stats['total_products']), "#2b719e"),
            ("📡", "Active RFID Tags", str(stats['total_rfid']), "#8e44ad"),
            ("⚠️", "Low Stock Alerts", str(stats['low_stock_alerts']), "#e67e22"),
            ("🚫", "Expired Items", str(stats['expired_items']), "#e74c3c"),
        ]
        for i, (icon, label, value, color) in enumerate(data):
            card = ctk.CTkFrame(sf, corner_radius=10, fg_color="#1a1a2e",
                                border_width=1, border_color="#2b2b4a")
            card.grid(row=0, column=i, padx=6, sticky="ew")
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=10),
                         text_color="#7a7a9e").pack(pady=(0, 12))

    def _build_content(self):
        cf = ctk.CTkFrame(self, fg_color="transparent")
        cf.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        cf.grid_columnconfigure(0, weight=3)
        cf.grid_columnconfigure(1, weight=2)
        cf.grid_rowconfigure(0, weight=1)
        self._build_users_panel(cf)
        self._build_settings_panel(cf)

    def _build_users_panel(self, parent):
        self.users_card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1a1a2e",
                                       border_width=1, border_color="#2b2b4a")
        self.users_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        hdr = ctk.CTkFrame(self.users_card, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(15, 10))
        ctk.CTkLabel(hdr, text="👥  User Management",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#e0e0ff").pack(side="left")
        ctk.CTkButton(hdr, text="+ Add User", width=100, height=30, corner_radius=6,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      fg_color="#2b719e", hover_color="#1f538d",
                      command=self._open_add_user_dialog).pack(side="right")

        th = ctk.CTkFrame(self.users_card, fg_color="#16162a", corner_radius=6)
        th.pack(fill="x", padx=15, pady=(0, 5))
        for text, w in [("ID", 40), ("Username", 110), ("Full Name", 150), ("Role", 80), ("Actions", 130)]:
            ctk.CTkLabel(th, text=text, width=w, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#7a7a9e").pack(side="left", padx=6, pady=8)

        self.users_list = ctk.CTkScrollableFrame(self.users_card, fg_color="transparent")
        self.users_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self._populate_users()

    def _populate_users(self):
        for w in self.users_list.winfo_children():
            w.destroy()

        current_uid = self.current_user[0] if self.current_user else None

        for uid, uname, role, full_name in get_all_users():
            row = ctk.CTkFrame(self.users_list, fg_color="#1e1e38", corner_radius=6, height=42)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            rc = "#2ecc71" if role == "admin" else "#3498db"
            rb = f"🛡️ {role.upper()}" if role == "admin" else f"👤 {role.upper()}"

            ctk.CTkLabel(row, text=str(uid), width=40, font=ctk.CTkFont(size=12),
                         text_color="#a0a0c0").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=uname, width=110, font=ctk.CTkFont(size=12),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=full_name, width=150, font=ctk.CTkFont(size=12),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rb, width=80, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=rc).pack(side="left", padx=6)

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=4)

            ctk.CTkButton(btn_frame, text="🔑", width=32, height=28, corner_radius=6,
                          font=ctk.CTkFont(size=13),
                          fg_color="#8e44ad", hover_color="#6c3483",
                          command=lambda u=uid, n=uname: self._open_change_password_dialog(u, n)
                          ).pack(side="left", padx=2)

            is_self = (uid == current_uid)
            ctk.CTkButton(btn_frame, text="🗑️", width=32, height=28, corner_radius=6,
                          font=ctk.CTkFont(size=13),
                          fg_color="#e74c3c" if not is_self else "#3b3b5a",
                          hover_color="#c0392b" if not is_self else "#3b3b5a",
                          state="normal" if not is_self else "disabled",
                          command=lambda u=uid, n=uname: self._confirm_delete_user(u, n)
                          ).pack(side="left", padx=2)

    def _open_add_user_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("420x510")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.lift()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="➕  Add New User",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(25, 20))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="Full Name", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        full_name_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                       border_color="#2b2b4a", fg_color="#16162a",
                                       placeholder_text="e.g. Dr. Ahmet Yılmaz")
        full_name_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(form, text="Username", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        username_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                      border_color="#2b2b4a", fg_color="#16162a",
                                      placeholder_text="e.g. ahmet")
        username_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(form, text="Password", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        password_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                      border_color="#2b2b4a", fg_color="#16162a",
                                      show="●", placeholder_text="Min. 6 characters")
        password_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(form, text="Role", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        role_var = ctk.StringVar(value="staff")
        role_seg = ctk.CTkSegmentedButton(form, values=["staff", "admin"],
                                          variable=role_var,
                                          selected_color="#2b719e",
                                          selected_hover_color="#1f538d",
                                          unselected_color="#2b2b4a",
                                          unselected_hover_color="#3b3b5a",
                                          font=ctk.CTkFont(size=13, weight="bold"))
        role_seg.pack(fill="x", pady=(0, 8))

        feedback = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12),
                                text_color="#e74c3c")
        feedback.pack(pady=(4, 0))

        def _save():
            full_name = full_name_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()

            if not full_name or not username or not password:
                feedback.configure(text="⚠️ All fields are required.", text_color="#e74c3c")
                return
            if len(password) < 6:
                feedback.configure(text="⚠️ Password must be at least 6 characters.", text_color="#e74c3c")
                return

            success = add_user(username, password, role, full_name)
            if not success:
                feedback.configure(text=f"⚠️ Username '{username}' already exists.", text_color="#e74c3c")
                return

            feedback.configure(text="✅ User created successfully!", text_color="#2ecc71")
            self._populate_users()
            dialog.after(1000, dialog.destroy)

        ctk.CTkButton(dialog, text="✅  Create User", height=42, corner_radius=8,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#2b719e", hover_color="#1f538d",
                      command=_save).pack(padx=30, pady=(16, 8), fill="x")

        ctk.CTkButton(dialog, text="Cancel", height=36, corner_radius=8,
                      font=ctk.CTkFont(size=13),
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      command=dialog.destroy).pack(padx=30, fill="x")

    def _open_change_password_dialog(self, user_id, username):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.lift()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="🔑  Change Password",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(25, 5))
        ctk.CTkLabel(dialog, text=f"User: {username}",
                     font=ctk.CTkFont(size=13),
                     text_color="#7a7a9e").pack(pady=(0, 20))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="New Password", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        pw_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                border_color="#2b2b4a", fg_color="#16162a",
                                show="●", placeholder_text="Min. 6 characters")
        pw_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(form, text="Confirm Password", font=ctk.CTkFont(size=13),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 4))
        pw_confirm = ctk.CTkEntry(form, height=38, corner_radius=8,
                                  border_color="#2b2b4a", fg_color="#16162a",
                                  show="●", placeholder_text="Repeat password")
        pw_confirm.pack(fill="x", pady=(0, 8))

        feedback = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        feedback.pack(pady=(4, 0))

        def _save():
            pw = pw_entry.get().strip()
            pw2 = pw_confirm.get().strip()
            if len(pw) < 6:
                feedback.configure(text="⚠️ Min. 6 characters required.", text_color="#e74c3c")
                return
            if pw != pw2:
                feedback.configure(text="⚠️ Passwords do not match.", text_color="#e74c3c")
                return
            update_user_password(user_id, pw)
            feedback.configure(text="✅ Password updated!", text_color="#2ecc71")
            dialog.after(1000, dialog.destroy)

        ctk.CTkButton(dialog, text="🔑  Update Password", height=42, corner_radius=8,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#8e44ad", hover_color="#6c3483",
                      command=_save).pack(padx=30, pady=(16, 8), fill="x")

        ctk.CTkButton(dialog, text="Cancel", height=36, corner_radius=8,
                      font=ctk.CTkFont(size=13),
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      command=dialog.destroy).pack(padx=30, fill="x")

    def _confirm_delete_user(self, user_id, username):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete User")
        dialog.geometry("380x220")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.lift()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="🗑️  Delete User",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e74c3c").pack(pady=(30, 10))
        ctk.CTkLabel(dialog, text=f"Are you sure you want to delete\n\"{username}\"?\nThis action cannot be undone.",
                     font=ctk.CTkFont(size=13), text_color="#a0a0c0",
                     justify="center").pack(pady=(0, 25))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=30)

        def _delete():
            delete_user(user_id)
            self._populate_users()
            dialog.destroy()

        ctk.CTkButton(btn_row, text="🗑️ Delete", height=40, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#e74c3c", hover_color="#c0392b",
                      command=_delete).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(btn_row, text="Cancel", height=40, corner_radius=8,
                      font=ctk.CTkFont(size=13),
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      command=dialog.destroy).pack(side="left", expand=True, padx=(5, 0))

    def _build_settings_panel(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1a1a2e",
                            border_width=1, border_color="#2b2b4a")
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(card, text="⚙️  System Settings",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(15, 20), padx=15, anchor="w")

        settings = get_system_settings()

        ctk.CTkLabel(card, text="Low Stock Threshold", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").pack(padx=20, anchor="w")
        tf = ctk.CTkFrame(card, fg_color="transparent")
        tf.pack(fill="x", padx=20, pady=(5, 15))
        self.threshold_slider = ctk.CTkSlider(tf, from_=5, to=100, number_of_steps=19,
                                              button_color="#2b719e", button_hover_color="#1f538d",
                                              progress_color="#2b719e", command=self._upd_thr)
        self.threshold_slider.set(int(settings.get('low_stock_threshold', '20')))
        self.threshold_slider.pack(side="left", fill="x", expand=True)
        self.thr_label = ctk.CTkLabel(tf, text=f"{settings.get('low_stock_threshold', '20')} units",
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      text_color="#e0e0ff", width=70)
        self.thr_label.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(card, text="Expiry Warning Period", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").pack(padx=20, anchor="w", pady=(10, 0))
        ef = ctk.CTkFrame(card, fg_color="transparent")
        ef.pack(fill="x", padx=20, pady=(5, 15))
        self.expiry_slider = ctk.CTkSlider(ef, from_=30, to=365, number_of_steps=11,
                                           button_color="#e67e22", button_hover_color="#d35400",
                                           progress_color="#e67e22", command=self._upd_exp)
        self.expiry_slider.set(int(settings.get('expiry_warning_days', '90')))
        self.expiry_slider.pack(side="left", fill="x", expand=True)
        self.exp_label = ctk.CTkLabel(ef, text=f"{settings.get('expiry_warning_days', '90')} days",
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      text_color="#e0e0ff", width=70)
        self.exp_label.pack(side="right", padx=(10, 0))

        ctk.CTkFrame(card, height=1, fg_color="#2b2b4a").pack(fill="x", padx=20, pady=10)

        self.save_btn = ctk.CTkButton(card, text="💾  Save Settings", height=38, corner_radius=8,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color="#2b719e", hover_color="#1f538d",
                                      command=self._save)
        self.save_btn.pack(padx=20, pady=(5, 15), fill="x")

    def _build_logs(self):
        card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a2e",
                            border_width=1, border_color="#2b2b4a")
        card.grid(row=3, column=0, sticky="nsew", pady=(8, 0))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(hdr, text="📜  Transaction Logs",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#e0e0ff").pack(side="left")

        ctk.CTkButton(hdr, text="🔄 Refresh", width=90, height=28, corner_radius=6,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      command=self._refresh_logs).pack(side="right")

        th = ctk.CTkFrame(card, fg_color="#16162a", corner_radius=6)
        th.pack(fill="x", padx=15, pady=(0, 5))

        for text, w in [("#", 35), ("Date & Time", 160), ("Staff", 150),
                        ("Medicine", 120), ("RFID Tag", 110), ("Action", 100)]:
            ctk.CTkLabel(th, text=text, width=w, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#7a7a9e").pack(side="left", padx=6, pady=8)

        self.logs_body = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.logs_body.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        self._populate_logs()

    def _populate_logs(self):
        for w in self.logs_body.winfo_children():
            w.destroy()

        movements = get_all_movements()

        if not movements:
            ctk.CTkLabel(self.logs_body,
                         text="📭  No transactions recorded yet.\nStaff must scan RFID tags to generate logs.",
                         font=ctk.CTkFont(size=13), text_color="#7a7a9e",
                         justify="center").pack(pady=20, expand=True)
            return

        for idx, (mid, rfid_tag, product_name, action, user_name, date) in enumerate(movements, 1):
            bg = "#1e1e38" if idx % 2 == 0 else "#1a1a30"
            row = ctk.CTkFrame(self.logs_body, fg_color=bg, corner_radius=6, height=36)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(idx), width=35,
                         font=ctk.CTkFont(size=11), text_color="#7a7a9e").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=date or "-", width=160,
                         font=ctk.CTkFont(size=11, family="Courier"),
                         text_color="#a8c7fa").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=user_name or "Unknown", width=150,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=product_name or "-", width=120,
                         font=ctk.CTkFont(size=11),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rfid_tag or "-", width=110,
                         font=ctk.CTkFont(size=11, family="Courier"),
                         text_color="#a0a0c0").pack(side="left", padx=6)

            if action == "DISPENSED":
                a_color, a_text = "#e67e22", "📤 Dispensed"
            elif action == "RETURNED":
                a_color, a_text = "#2ecc71", "📥 Returned"
            elif action == "ADDED":
                a_color, a_text = "#3498db", "➕ Added"
            else:
                a_color, a_text = "#7a7a9e", f"⚡ {action}"

            ctk.CTkLabel(row, text=a_text, width=100,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=a_color).pack(side="left", padx=6)

    def _refresh_logs(self):
        self._populate_logs()

    def _upd_thr(self, v):
        self.thr_label.configure(text=f"{int(v)} units")

    def _upd_exp(self, v):
        self.exp_label.configure(text=f"{int(v)} days")

    def _save(self):
        update_system_setting('low_stock_threshold', int(self.threshold_slider.get()))
        update_system_setting('expiry_warning_days', int(self.expiry_slider.get()))
        self.save_btn.configure(text="✓ Saved!", fg_color="#2ecc71")
        self.after(2000, lambda: self.save_btn.configure(text="💾  Save Settings", fg_color="#2b719e"))
