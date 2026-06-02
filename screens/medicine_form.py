import customtkinter as ctk
import theme as T
from database import add_medicine, log_movement


class MedicineForm(ctk.CTkFrame):

    def __init__(self, parent, on_back, current_user=None):
        super().__init__(parent, fg_color=T.BG_PRIMARY)
        self.on_back = on_back
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_form()

    # ─── Header / Navbar ──────────────────────────────────────────────────────
    def _build_header(self):
        hdr = T.navbar(self)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hdr, text="New Medicine",
            font=T.headline(), text_color=T.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=16, sticky="w")

        T.secondary_button(
            hdr, text="← Back", width=80, height=32,
            command=self.on_back
        ).grid(row=0, column=2, padx=16, pady=12)

    # ─── Form Body ────────────────────────────────────────────────────────────
    def _build_form(self):
        outer = T.card(self)
        outer.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(
            outer, text="Register New Medicine",
            font=T.headline(), text_color=T.TEXT_PRIMARY
        ).pack(pady=(28, 4))

        ctk.CTkLabel(
            outer, text="Fill in the details below to add a medicine to inventory.",
            font=T.callout(), text_color=T.TEXT_SECONDARY
        ).pack(pady=(0, 20))

        T.separator(outer).pack(fill="x", padx=32, pady=(0, 24))

        form = ctk.CTkFrame(outer, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40, pady=(0, 16))
        form.grid_columnconfigure((0, 1), weight=1)

        # Row 1
        self._label(form, "Medicine Name *", row=0, col=0)
        self.name_entry = T.text_input(form, placeholder="e.g. Paracetamol", height=44)
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(0, 16))

        self._label(form, "Batch Number *", row=0, col=1)
        self.batch_entry = T.text_input(form, placeholder="e.g. B-2025-001", height=44)
        self.batch_entry.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 16))

        # Row 2
        self._label(form, "Expiry Date *", row=2, col=0)
        self.expiry_entry = T.text_input(form, placeholder="YYYY-MM  (e.g. 2027-06)", height=44)
        self.expiry_entry.grid(row=3, column=0, sticky="ew", padx=(0, 12), pady=(0, 16))

        self._label(form, "Initial Quantity *", row=2, col=1)
        self.qty_entry = T.text_input(form, placeholder="e.g. 100", height=44)
        self.qty_entry.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(0, 16))

        # RFID Tag row (full-width)
        self._label(form, "RFID Tag Assignment", row=4, col=0)
        rfid_row = ctk.CTkFrame(form, fg_color="transparent")
        rfid_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.rfid_entry = T.text_input(rfid_row, placeholder="Scan or enter RFID tag...", height=44)
        self.rfid_entry.pack(side="left", fill="x", expand=True)

        self.scan_btn = ctk.CTkButton(
            rfid_row, text="Scan Tag", width=110, height=44,
            corner_radius=T.RADIUS_MD,
            fg_color=T.PURPLE, hover_color=T.PURPLE_HOVER,
            text_color=T.TEXT_PRIMARY, font=T.callout_bold(),
            command=self._simulate_scan
        )
        self.scan_btn.pack(side="right", padx=(10, 0))

        self.rfid_status = ctk.CTkLabel(
            form, text="", font=T.footnote(), text_color=T.TEXT_SECONDARY
        )
        self.rfid_status.grid(row=6, column=0, sticky="w")

        # Separator + buttons
        T.separator(outer).pack(fill="x", padx=40, pady=(8, 16))

        self.feedback = ctk.CTkLabel(
            outer, text="", font=T.callout_bold()
        )
        self.feedback.pack(pady=(0, 8))

        btns = ctk.CTkFrame(outer, fg_color="transparent")
        btns.pack(pady=(0, 32))

        T.secondary_button(
            btns, text="Cancel", width=140, height=44,
            command=self._cancel
        ).pack(side="left", padx=(0, 12))

        self.save_btn = T.primary_button(
            btns, text="Save Medicine", width=190, height=44,
            command=self._save
        )
        self.save_btn.pack(side="left")

    def _label(self, parent, text, row, col):
        ctk.CTkLabel(
            parent, text=text, font=T.callout_bold(),
            text_color=T.TEXT_SECONDARY
        ).grid(row=row, column=col, sticky="w",
               padx=(0, 12) if col == 0 else (12, 0),
               pady=(0, 4))

    # ─── Actions ──────────────────────────────────────────────────────────────
    def _simulate_scan(self):
        import random
        tag = f"RFID-{random.randint(1000, 9999)}"
        self.rfid_entry.delete(0, "end")
        self.rfid_entry.insert(0, tag)
        self.rfid_status.configure(text=f"Tag detected: {tag}", text_color=T.GREEN)
        self.scan_btn.configure(text="Scanned", fg_color=T.GREEN, hover_color=T.GREEN_HOVER)
        self.after(2000, lambda: self.scan_btn.configure(
            text="Scan Tag", fg_color=T.PURPLE, hover_color=T.PURPLE_HOVER
        ))

    def _save(self):
        name   = self.name_entry.get().strip()
        batch  = self.batch_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        qty    = self.qty_entry.get().strip()
        rfid   = self.rfid_entry.get().strip()

        required = [
            (self.name_entry,   name),
            (self.batch_entry,  batch),
            (self.expiry_entry, expiry),
            (self.qty_entry,    qty),
        ]
        missing = any(not v for _, v in required)
        if missing:
            self.feedback.configure(text="Please fill in all required fields.", text_color=T.RED)
            for entry, val in required:
                entry.configure(border_color=T.RED if not val else T.BORDER)
            return

        try:
            qty_int = int(qty)
        except ValueError:
            self.feedback.configure(text="Quantity must be a number.", text_color=T.RED)
            self.qty_entry.configure(border_color=T.RED)
            return

        add_medicine(name, batch, expiry, qty_int, rfid)
        log_movement(rfid_tag=rfid or "-", product_name=name,
                     action="ADDED", user=self.current_user)

        self.save_btn.configure(text="Saved", fg_color=T.GREEN, hover_color=T.GREEN_HOVER)
        self.feedback.configure(text=f"{name} registered successfully.", text_color=T.GREEN)
        self.after(1500, self._clear_form)

    def _cancel(self):
        self._clear_form()
        self.on_back()

    def _clear_form(self):
        for entry in [self.name_entry, self.batch_entry,
                      self.expiry_entry, self.qty_entry, self.rfid_entry]:
            entry.delete(0, "end")
            entry.configure(border_color=T.BORDER)
        self.feedback.configure(text="")
        self.rfid_status.configure(text="")
        self.save_btn.configure(text="Save Medicine", fg_color=T.BLUE, hover_color=T.BLUE_HOVER)
