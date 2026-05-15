import customtkinter as ctk
from database import add_medicine


class MedicineForm(ctk.CTkFrame):
    """Figure 21: Medicine Registration and Edit Form"""

    def __init__(self, parent, on_back):
        super().__init__(parent, fg_color="transparent")
        self.on_back = on_back
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_form()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, height=50, corner_radius=10, fg_color="#1a1a2e",
                           border_width=1, border_color="#2b2b4a")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="💊  Medicine Registration",
                     font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
                     text_color="#e0e0ff").grid(row=0, column=0, padx=20, pady=12, sticky="w")

        ctk.CTkButton(hdr, text="← Back", width=80, height=34, corner_radius=8,
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.on_back).grid(row=0, column=2, padx=15, pady=10)

    def _build_form(self):
        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1a1a2e",
                            border_width=1, border_color="#2b2b4a")
        card.grid(row=1, column=0, sticky="nsew")

        # Form title
        ctk.CTkLabel(card, text="Register New Medicine",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(25, 5))
        ctk.CTkLabel(card, text="Fill in the details below to add a new medicine to the system",
                     font=ctk.CTkFont(size=12), text_color="#7a7a9e").pack(pady=(0, 20))

        ctk.CTkFrame(card, height=1, fg_color="#2b2b4a").pack(fill="x", padx=30, pady=(0, 20))

        # 2 sütunlu form layout
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40, pady=(0, 10))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        # ROW 0: Medicine Name
        ctk.CTkLabel(form, text="Medicine Name *", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").grid(row=0, column=0, sticky="w", padx=10, pady=(0, 3))
        self.name_entry = ctk.CTkEntry(form, placeholder_text="e.g. Paracetamol",
                                       height=42, corner_radius=8,
                                       border_color="#2b2b4a", fg_color="#16162a",
                                       font=ctk.CTkFont(size=14))
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))

        # ROW 0: Batch No
        ctk.CTkLabel(form, text="Batch Number *", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").grid(row=0, column=1, sticky="w", padx=10, pady=(0, 3))
        self.batch_entry = ctk.CTkEntry(form, placeholder_text="e.g. B-2025-001",
                                        height=42, corner_radius=8,
                                        border_color="#2b2b4a", fg_color="#16162a",
                                        font=ctk.CTkFont(size=14))
        self.batch_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 15))

        # ROW 2: Expiry Date
        ctk.CTkLabel(form, text="Expiry Date *", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 3))
        self.expiry_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM  (e.g. 2027-06)",
                                         height=42, corner_radius=8,
                                         border_color="#2b2b4a", fg_color="#16162a",
                                         font=ctk.CTkFont(size=14))
        self.expiry_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 15))

        # ROW 2: Quantity
        ctk.CTkLabel(form, text="Initial Quantity *", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").grid(row=2, column=1, sticky="w", padx=10, pady=(0, 3))
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="e.g. 100",
                                      height=42, corner_radius=8,
                                      border_color="#2b2b4a", fg_color="#16162a",
                                      font=ctk.CTkFont(size=14))
        self.qty_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 15))

        # ROW 4: RFID Tag Assignment (full width)
        ctk.CTkLabel(form, text="RFID Tag Assignment", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#a0a0c0").grid(row=4, column=0, sticky="w", padx=10, pady=(5, 3))

        rfid_frame = ctk.CTkFrame(form, fg_color="transparent")
        rfid_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))

        self.rfid_entry = ctk.CTkEntry(rfid_frame, placeholder_text="Scan or enter RFID tag...",
                                       height=42, corner_radius=8,
                                       border_color="#2b2b4a", fg_color="#16162a",
                                       font=ctk.CTkFont(size=14))
        self.rfid_entry.pack(side="left", fill="x", expand=True)

        self.scan_btn = ctk.CTkButton(rfid_frame, text="📡 Scan Tag", width=120, height=42,
                                      corner_radius=8,
                                      fg_color="#8e44ad", hover_color="#7d3c98",
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      command=self._simulate_scan)
        self.scan_btn.pack(side="right", padx=(10, 0))

        # RFID status
        self.rfid_status = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11),
                                        text_color="#7a7a9e")
        self.rfid_status.grid(row=6, column=0, sticky="w", padx=10)

        # Divider
        div = ctk.CTkFrame(card, height=1, fg_color="#2b2b4a")
        div.pack(fill="x", padx=40, pady=(10, 15))

        # Feedback label
        self.feedback = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.feedback.pack(pady=(0, 5))

        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(0, 30))

        ctk.CTkButton(btn_frame, text="Cancel", width=140, height=42, corner_radius=8,
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._cancel).pack(side="left", padx=8)

        self.save_btn = ctk.CTkButton(btn_frame, text="💾  Save Medicine", width=200, height=42,
                                      corner_radius=8,
                                      fg_color="#2b719e", hover_color="#1f538d",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      command=self._save)
        self.save_btn.pack(side="left", padx=8)

    def _simulate_scan(self):
        """RFID okutma simülasyonu"""
        import random
        tag = f"RFID-{random.randint(1000, 9999)}"
        self.rfid_entry.delete(0, "end")
        self.rfid_entry.insert(0, tag)
        self.rfid_status.configure(text=f"✓ Tag detected: {tag}", text_color="#2ecc71")
        self.scan_btn.configure(text="✓ Scanned", fg_color="#2ecc71")
        self.after(2000, lambda: self.scan_btn.configure(text="📡 Scan Tag", fg_color="#8e44ad"))

    def _save(self):
        """Formu kaydet"""
        name = self.name_entry.get().strip()
        batch = self.batch_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        qty = self.qty_entry.get().strip()
        rfid = self.rfid_entry.get().strip()

        # Validation
        if not name or not batch or not expiry or not qty:
            self.feedback.configure(text="⚠ Please fill in all required fields (*)", text_color="#e74c3c")
            # Highlight empty fields
            for entry, val in [(self.name_entry, name), (self.batch_entry, batch),
                               (self.expiry_entry, expiry), (self.qty_entry, qty)]:
                if not val:
                    entry.configure(border_color="#e74c3c")
                else:
                    entry.configure(border_color="#2b2b4a")
            return

        try:
            qty_int = int(qty)
        except ValueError:
            self.feedback.configure(text="⚠ Quantity must be a number", text_color="#e74c3c")
            self.qty_entry.configure(border_color="#e74c3c")
            return

        add_medicine(name, batch, expiry, qty_int, rfid)
        self.save_btn.configure(text="✓ Saved!", fg_color="#2ecc71")
        self.feedback.configure(text=f"✓ {name} registered successfully!", text_color="#2ecc71")

        # Formu temizle
        self.after(1500, self._clear_form)

    def _cancel(self):
        self._clear_form()
        self.on_back()

    def _clear_form(self):
        for entry in [self.name_entry, self.batch_entry, self.expiry_entry,
                      self.qty_entry, self.rfid_entry]:
            entry.delete(0, "end")
            entry.configure(border_color="#2b2b4a")
        self.feedback.configure(text="")
        self.rfid_status.configure(text="")
        self.save_btn.configure(text="💾  Save Medicine", fg_color="#2b719e")
