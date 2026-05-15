import customtkinter as ctk
from database import get_all_inventory, delete_medicine, get_medicine_details, update_medicine


class StaffInventory(ctk.CTkFrame):
    """Figure 19: Staff Dashboard and Inventory Table"""

    def __init__(self, parent, on_logout, on_switch_scanner, on_add_medicine, current_user=None):
        super().__init__(parent, fg_color="transparent")
        self.on_logout = on_logout
        self.on_switch_scanner = on_switch_scanner
        self.on_add_medicine = on_add_medicine
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_navbar()
        self._build_tabs()
        self._build_table()

    def _build_navbar(self):
        nav = ctk.CTkFrame(self, height=50, corner_radius=10, fg_color="#1a1a2e",
                           border_width=1, border_color="#2b2b4a")
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(nav, text="📋  Staff Dashboard",
                     font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
                     text_color="#e0e0ff").grid(row=0, column=0, padx=20, pady=12, sticky="w")

        name = self.current_user[3] if self.current_user else "Staff"
        ctk.CTkLabel(nav, text=f"👤 {name}", font=ctk.CTkFont(size=13),
                     text_color="#7a7a9e").grid(row=0, column=1, sticky="e", padx=5)

        ctk.CTkButton(nav, text="⏻ Logout", width=100, height=34, corner_radius=8,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.on_logout).grid(row=0, column=2, padx=15, pady=10)

    def _build_tabs(self):
        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.tab_inventory = ctk.CTkButton(
            tab_frame, text="📋 Inventory", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2b719e", hover_color="#1f538d")
        self.tab_inventory.pack(side="left", padx=(0, 5))

        self.tab_scanner = ctk.CTkButton(
            tab_frame, text="📡 RFID Scanner", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2b2b4a", hover_color="#3b3b5a",
            command=self.on_switch_scanner)
        self.tab_scanner.pack(side="left", padx=5)

        self.add_btn = ctk.CTkButton(
            tab_frame, text="+ Add Medicine", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2ecc71", hover_color="#27ae60",
            command=self.on_add_medicine)
        self.add_btn.pack(side="right")

        # Search bar
        self.search_entry = ctk.CTkEntry(
            tab_frame, placeholder_text="🔍 Search medicines...",
            width=220, height=36, corner_radius=8,
            border_color="#2b2b4a", fg_color="#16162a")
        self.search_entry.pack(side="right", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._filter_table)

    def _build_table(self):
        self.table_card = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a2e",
                            border_width=1, border_color="#2b2b4a")
        self.table_card.grid(row=2, column=0, sticky="nsew")

        # Table header
        th = ctk.CTkFrame(self.table_card, fg_color="#16162a", corner_radius=8)
        th.pack(fill="x", padx=15, pady=(15, 5))

        cols = [("#", 35), ("Medicine Name", 140), ("Batch No", 100),
                ("Stock", 70), ("Expiry", 100), ("Status", 100), ("Actions", 100)]
        for text, w in cols:
            ctk.CTkLabel(th, text=text, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#7a7a9e").pack(side="left", padx=6, pady=10)

        # Table body
        self.table_body = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Feedback label
        self.feedback_label = ctk.CTkLabel(self.table_card, text="", font=ctk.CTkFont(size=12))
        self.feedback_label.pack(pady=(0, 10))

        self._populate_rows()

    def _populate_rows(self, filter_text=""):
        for w in self.table_body.winfo_children():
            w.destroy()

        inventory = get_all_inventory()
        for idx, (product_id, name, batch, qty, expiry, status) in enumerate(inventory, 1):
            if filter_text and filter_text.lower() not in name.lower():
                continue

            bg = "#1e1e38" if idx % 2 == 0 else "#1a1a30"
            row = ctk.CTkFrame(self.table_body, fg_color=bg, corner_radius=6, height=42)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(idx), width=35,
                         font=ctk.CTkFont(size=12), text_color="#7a7a9e").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=name, width=140,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=batch, width=100,
                         font=ctk.CTkFont(size=12, family="Courier"),
                         text_color="#a8c7fa").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=str(qty), width=70,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#e0e0ff").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=expiry, width=100,
                         font=ctk.CTkFont(size=12),
                         text_color="#a0a0c0").pack(side="left", padx=6)

            # Status badge
            if status == "Expired":
                s_color, s_text = "#e74c3c", "🔴 Expired"
            elif status == "Low Stock":
                s_color, s_text = "#e67e22", "🟠 Low Stock"
            else:
                s_color, s_text = "#2ecc71", "🟢 In Stock"

            ctk.CTkLabel(row, text=s_text, width=100,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=s_color).pack(side="left", padx=6)

            # Action buttons frame
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="left", padx=6)

            # ✏️ Edit button
            ctk.CTkButton(actions, text="✏️", width=36, height=28, corner_radius=6,
                          fg_color="#1a3a5c", hover_color="#2b719e",
                          font=ctk.CTkFont(size=13),
                          command=lambda pid=product_id: self._open_edit(pid)
                          ).pack(side="left", padx=(0, 4))

            # 🗑️ Delete button
            ctk.CTkButton(actions, text="🗑️", width=36, height=28, corner_radius=6,
                          fg_color="#3a1a1a", hover_color="#e74c3c",
                          font=ctk.CTkFont(size=13),
                          command=lambda pid=product_id, n=name: self._confirm_delete(pid, n)
                          ).pack(side="left")

    # ==========================================
    # DÜZENLEME (Edit) İşlemleri
    # ==========================================
    def _open_edit(self, product_id):
        """Düzenleme penceresi aç"""
        details = get_medicine_details(product_id)
        if not details:
            return

        pid, name, batch_code, qty, expiry, batch_id = details

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Medicine")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Header
        ctk.CTkLabel(dialog, text="✏️  Edit Medicine",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(20, 5))
        ctk.CTkFrame(dialog, height=1, fg_color="#2b2b4a").pack(fill="x", padx=25, pady=(5, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Medicine Name
        ctk.CTkLabel(form, text="Medicine Name", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 3))
        name_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                  border_color="#2b2b4a", fg_color="#16162a",
                                  font=ctk.CTkFont(size=13))
        name_entry.insert(0, name)
        name_entry.pack(fill="x", pady=(0, 12))

        # Batch No
        ctk.CTkLabel(form, text="Batch Number", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#a0a0c0").pack(anchor="w", pady=(0, 3))
        batch_entry = ctk.CTkEntry(form, height=38, corner_radius=8,
                                   border_color="#2b2b4a", fg_color="#16162a",
                                   font=ctk.CTkFont(size=13))
        batch_entry.insert(0, batch_code)
        batch_entry.pack(fill="x", pady=(0, 12))

        # 2-column: Expiry + Quantity
        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 12))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row2, text="Expiry Date", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#a0a0c0").grid(row=0, column=0, sticky="w", padx=(0, 5))
        expiry_entry = ctk.CTkEntry(row2, height=38, corner_radius=8,
                                    border_color="#2b2b4a", fg_color="#16162a",
                                    font=ctk.CTkFont(size=13))
        expiry_entry.insert(0, expiry)
        expiry_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(row2, text="Quantity", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#a0a0c0").grid(row=0, column=1, sticky="w", padx=(5, 0))
        qty_entry = ctk.CTkEntry(row2, height=38, corner_radius=8,
                                 border_color="#2b2b4a", fg_color="#16162a",
                                 font=ctk.CTkFont(size=13))
        qty_entry.insert(0, str(qty))
        qty_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        # Error label
        err_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=11), text_color="#e74c3c")
        err_label.pack(pady=(5, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))

        ctk.CTkButton(btn_frame, text="Cancel", width=130, height=38,
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=dialog.destroy).pack(side="left", padx=8)

        def save_edit():
            n = name_entry.get().strip()
            b = batch_entry.get().strip()
            e = expiry_entry.get().strip()
            q = qty_entry.get().strip()
            if not n or not b or not e or not q:
                err_label.configure(text="⚠ All fields are required")
                return
            try:
                q_int = int(q)
            except ValueError:
                err_label.configure(text="⚠ Quantity must be a number")
                return
            update_medicine(pid, n, b, e, q_int)
            dialog.destroy()
            self.feedback_label.configure(text=f"✓ {n} updated successfully", text_color="#2ecc71")
            self._populate_rows()
            self.after(3000, lambda: self.feedback_label.configure(text=""))

        ctk.CTkButton(btn_frame, text="💾 Save Changes", width=160, height=38,
                      fg_color="#2b719e", hover_color="#1f538d",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=save_edit).pack(side="left", padx=8)

    # ==========================================
    # SİLME (Delete) İşlemleri
    # ==========================================
    def _confirm_delete(self, product_id, name):
        """Silme onayı penceresi"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="⚠️ Delete Medicine",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e74c3c").pack(pady=(25, 10))

        ctk.CTkLabel(dialog, text=f'Are you sure you want to delete\n"{name}" from inventory?',
                     font=ctk.CTkFont(size=13), text_color="#a0a0c0").pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Cancel", width=120, height=36,
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=dialog.destroy).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="🗑️ Delete", width=120, height=36,
                      fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=lambda: self._do_delete(product_id, name, dialog)
                      ).pack(side="left", padx=8)

    def _do_delete(self, product_id, name, dialog):
        delete_medicine(product_id)
        dialog.destroy()
        self.feedback_label.configure(text=f"✓ {name} deleted successfully", text_color="#2ecc71")
        self._populate_rows()
        self.after(3000, lambda: self.feedback_label.configure(text=""))

    def _filter_table(self, event=None):
        text = self.search_entry.get()
        self._populate_rows(text)

    def refresh(self):
        """Tabloyu yeniler"""
        self._populate_rows()
