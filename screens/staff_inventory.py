import customtkinter as ctk
import theme as T
from database import get_all_inventory, delete_medicine, get_medicine_details, update_medicine


class StaffInventory(ctk.CTkFrame):

    def __init__(self, parent, on_logout, on_switch_scanner, on_add_medicine, current_user=None):
        super().__init__(parent, fg_color=T.BG_PRIMARY)
        self.on_logout = on_logout
        self.on_switch_scanner = on_switch_scanner
        self.on_add_medicine = on_add_medicine
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build_navbar()
        self._build_toolbar()
        self._build_table()

    # ─── Navbar ───────────────────────────────────────────────────────────────
    def _build_navbar(self):
        nav = T.navbar(self)
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            nav, text="Inventory",
            font=T.headline(), text_color=T.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=16, sticky="w")

        name = self.current_user[3] if self.current_user else "Staff"
        ctk.CTkLabel(
            nav, text=name,
            font=T.callout(), text_color=T.TEXT_SECONDARY
        ).grid(row=0, column=1, sticky="e", padx=12)

        T.danger_button(
            nav, text="Sign Out", width=90, height=32,
            command=self.on_logout
        ).grid(row=0, column=2, padx=16, pady=12)

    # ─── Toolbar (tabs + search + add) ────────────────────────────────────────
    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        bar.grid_columnconfigure(1, weight=1)

        # Left: tab segmented control
        seg = ctk.CTkFrame(
            bar, fg_color=T.BG_SECONDARY,
            corner_radius=T.RADIUS_MD,
            border_width=1, border_color=T.BORDER
        )
        seg.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            seg, text="Inventory", height=34, width=110,
            corner_radius=T.RADIUS_SM,
            fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
            text_color=T.TEXT_PRIMARY, font=T.callout_bold()
        ).pack(side="left", padx=6, pady=6)

        T.secondary_button(
            seg, text="RFID Scanner", height=34, width=120,
            command=self.on_switch_scanner
        ).pack(side="left", pady=6)

        # Right: search + add button
        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        self.search_entry = T.text_input(
            right, placeholder="Search medicines...",
            height=36, width=220
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._filter_table)

        T.primary_button(
            right, text="+ Add Medicine",
            height=36, width=130,
            fg_color=T.GREEN, hover_color=T.GREEN_HOVER,
            command=self.on_add_medicine
        ).pack(side="left")

    # ─── Main Table ───────────────────────────────────────────────────────────
    def _build_table(self):
        self.table_card = T.card(self)
        self.table_card.grid(row=2, column=0, sticky="nsew")
        self.table_card.grid_rowconfigure(1, weight=1)
        self.table_card.grid_columnconfigure(0, weight=1)

        # Header row
        th = ctk.CTkFrame(self.table_card, fg_color=T.BG_TERTIARY, corner_radius=T.RADIUS_SM)
        th.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 6))

        cols = [
            ("#",            40),
            ("Medicine",     170),
            ("Batch",        110),
            ("Stock",        70),
            ("Expiry",       110),
            ("Status",       110),
            ("Actions",      110),
        ]
        for text, w in cols:
            ctk.CTkLabel(
                th, text=text, width=w,
                font=T.footnote(), text_color=T.TEXT_SECONDARY
            ).pack(side="left", padx=8, pady=9)

        # Scrollable body
        self.table_body = ctk.CTkScrollableFrame(
            self.table_card, fg_color="transparent"
        )
        self.table_body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 6))

        # Feedback
        self.feedback_label = ctk.CTkLabel(
            self.table_card, text="", font=T.callout()
        )
        self.feedback_label.grid(row=2, column=0, pady=(0, 10))

        self._populate_rows()

    def _populate_rows(self, filter_text=""):
        for w in self.table_body.winfo_children():
            w.destroy()

        inventory = get_all_inventory()
        shown = 0
        for idx, (product_id, name, batch, qty, expiry, status) in enumerate(inventory, 1):
            if filter_text and filter_text.lower() not in name.lower():
                continue
            shown += 1

            # Alternating row colors
            bg = T.BG_SECONDARY if shown % 2 == 1 else T.BG_TERTIARY
            row = ctk.CTkFrame(
                self.table_body, fg_color=bg,
                corner_radius=T.RADIUS_SM, height=46
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(idx), width=40,
                         font=T.caption(), text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=8)

            ctk.CTkLabel(row, text=name, width=170,
                         font=T.body_bold(), text_color=T.TEXT_PRIMARY
                         ).pack(side="left", padx=4)

            ctk.CTkLabel(row, text=batch, width=110,
                         font=ctk.CTkFont(family="SF Mono", size=11),
                         text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=4)

            qty_color = T.RED if qty == 0 else T.ORANGE if qty <= 20 else T.TEXT_PRIMARY
            ctk.CTkLabel(row, text=str(qty), width=70,
                         font=T.body_bold(), text_color=qty_color
                         ).pack(side="left", padx=4)

            ctk.CTkLabel(row, text=expiry, width=110,
                         font=T.footnote(), text_color=T.TEXT_SECONDARY
                         ).pack(side="left", padx=4)

            # Status badge
            badge_text, badge_bg, badge_fg = T.status_badge_colors(status)
            badge = ctk.CTkFrame(row, fg_color=badge_bg, corner_radius=T.RADIUS_SM, width=90, height=26)
            badge.pack(side="left", padx=10)
            badge.pack_propagate(False)
            ctk.CTkLabel(
                badge, text=badge_text,
                font=T.caption(), text_color=badge_fg
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Action buttons
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.pack(side="left", padx=4)

            ctk.CTkButton(
                act, text="Edit", width=48, height=28,
                corner_radius=T.RADIUS_SM,
                fg_color=T.BG_QUATERNARY, hover_color=T.BLUE,
                text_color=T.TEXT_SECONDARY, font=T.caption(),
                command=lambda pid=product_id: self._open_edit(pid)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                act, text="Delete", width=56, height=28,
                corner_radius=T.RADIUS_SM,
                fg_color=T.BG_QUATERNARY, hover_color=T.RED,
                text_color=T.TEXT_SECONDARY, font=T.caption(),
                command=lambda pid=product_id, n=name: self._confirm_delete(pid, n)
            ).pack(side="left")

        if shown == 0:
            ctk.CTkLabel(
                self.table_body,
                text="No medicines found.",
                font=T.callout(), text_color=T.TEXT_TERTIARY
            ).pack(pady=40)

    # ─── Edit Dialog ──────────────────────────────────────────────────────────
    def _open_edit(self, product_id):
        details = get_medicine_details(product_id)
        if not details:
            return
        pid, name, batch_code, qty, expiry, batch_id = details

        d = self._dialog("Edit Medicine", 440, 420)

        ctk.CTkLabel(d, text="Edit Medicine",
                     font=T.headline(), text_color=T.TEXT_PRIMARY
                     ).pack(pady=(28, 4))
        T.separator(d).pack(fill="x", padx=28, pady=(4, 20))

        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=28)

        name_entry = self._field(form, "Medicine Name", name)
        batch_entry = self._field(form, "Batch Number", batch_code)

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 8))
        row2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row2, text="Expiry Date", font=T.callout_bold(),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", padx=(0, 6))
        expiry_entry = T.text_input(row2, height=42)
        expiry_entry.insert(0, expiry)
        expiry_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(row2, text="Quantity", font=T.callout_bold(),
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=1, sticky="w", padx=(6, 0))
        qty_entry = T.text_input(row2, height=42)
        qty_entry.insert(0, str(qty))
        qty_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        err = ctk.CTkLabel(d, text="", font=T.footnote(), text_color=T.RED)
        err.pack(pady=(8, 0))

        btns = ctk.CTkFrame(d, fg_color="transparent")
        btns.pack(pady=(8, 24), fill="x", padx=28)

        T.secondary_button(btns, text="Cancel", width=130, height=42,
                           command=d.destroy).pack(side="left", padx=(0, 8))

        def _save():
            n = name_entry.get().strip()
            b = batch_entry.get().strip()
            e = expiry_entry.get().strip()
            q = qty_entry.get().strip()
            if not all([n, b, e, q]):
                err.configure(text="All fields are required.")
                return
            try:
                q_int = int(q)
            except ValueError:
                err.configure(text="Quantity must be a number.")
                return
            update_medicine(pid, n, b, e, q_int)
            d.destroy()
            self.feedback_label.configure(
                text=f"  {n} updated.", text_color=T.GREEN
            )
            self._populate_rows()
            self.after(3000, lambda: self.feedback_label.configure(text=""))

        T.primary_button(btns, text="Save Changes", width=160, height=42,
                         command=_save).pack(side="left")

    # ─── Delete Confirm ───────────────────────────────────────────────────────
    def _confirm_delete(self, product_id, name):
        d = self._dialog("Delete Medicine", 360, 210)

        ctk.CTkLabel(d, text="Delete Medicine",
                     font=T.headline(), text_color=T.RED
                     ).pack(pady=(28, 8))
        ctk.CTkLabel(
            d, text=f'Remove "{name}" from inventory?\nThis cannot be undone.',
            font=T.callout(), text_color=T.TEXT_SECONDARY, justify="center"
        ).pack(pady=(0, 24))

        btns = ctk.CTkFrame(d, fg_color="transparent")
        btns.pack(fill="x", padx=28)

        T.secondary_button(btns, text="Cancel", width=130, height=40,
                           command=d.destroy).pack(side="left", padx=(0, 8))
        T.danger_button(btns, text="Delete", width=130, height=40,
                        command=lambda: self._do_delete(product_id, name, d)
                        ).pack(side="left")

    def _do_delete(self, product_id, name, dialog):
        delete_medicine(product_id)
        dialog.destroy()
        self.feedback_label.configure(text=f"  {name} deleted.", text_color=T.GREEN)
        self._populate_rows()
        self.after(3000, lambda: self.feedback_label.configure(text=""))

    # ─── Helpers ──────────────────────────────────────────────────────────────
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

    def _field(self, parent, label_text, initial=""):
        ctk.CTkLabel(parent, text=label_text, font=T.callout_bold(),
                     text_color=T.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))
        e = T.text_input(parent, height=42)
        e.insert(0, initial)
        e.pack(fill="x", pady=(0, 14))
        return e

    def _filter_table(self, event=None):
        self._populate_rows(self.search_entry.get())

    def refresh(self):
        self._populate_rows()
