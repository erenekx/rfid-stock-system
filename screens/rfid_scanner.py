import customtkinter as ctk
import datetime
from rfid_simulator import scan_rfid


class RFIDScannerScreen(ctk.CTkFrame):
    """Figure 20: Staff Dashboard / RFID Scan Screen (mevcut kodun frame versiyonu)"""

    def __init__(self, parent, on_logout, on_switch_inventory, current_user=None):
        super().__init__(parent, fg_color="transparent")
        self.on_logout = on_logout
        self.on_switch_inventory = on_switch_inventory
        self.current_user = current_user

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_navbar()
        self._build_tabs()
        self._build_scanner()

    def _build_navbar(self):
        nav = ctk.CTkFrame(self, height=50, corner_radius=10, fg_color="#1a1a2e",
                           border_width=1, border_color="#2b2b4a")
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(nav, text="📡  RFID Scan & Stock Movement",
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

        ctk.CTkButton(tab_frame, text="📋 Inventory", height=36, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#2b2b4a", hover_color="#3b3b5a",
                      command=self.on_switch_inventory).pack(side="left", padx=(0, 5))

        ctk.CTkButton(tab_frame, text="📡 RFID Scanner", height=36, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#2b719e", hover_color="#1f538d").pack(side="left", padx=5)

    def _build_scanner(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=5)
        content.grid_columnconfigure(1, weight=4)
        content.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL ---
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Reader card
        reader = ctk.CTkFrame(left, corner_radius=10, fg_color="#1a1a2e",
                               border_width=1, border_color="#2b2b4a")
        reader.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(reader, text="Hardware Interface",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(15, 5))

        self.entry_rfid = ctk.CTkEntry(reader, placeholder_text="Waiting for EPC tag...",
                                       width=280, height=40,
                                       font=ctk.CTkFont(size=15), justify="center",
                                       border_color="#2b2b4a", fg_color="#16162a")
        self.entry_rfid.pack(pady=10)
        self.entry_rfid.bind("<Return>", self.auto_scan)

        ctk.CTkButton(reader, text="Simulate Tag Reading", height=40,
                      font=ctk.CTkFont(weight="bold"),
                      fg_color="#2b719e", hover_color="#1f538d",
                      command=self.zone_scan).pack(pady=(0, 15))

        # Status
        self.status_label = ctk.CTkLabel(left, text="🟢 Scanner Ready",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#2ecc71")
        self.status_label.pack(pady=5)

        # Result card
        self.result_card = ctk.CTkFrame(left, corner_radius=10, fg_color="#1a1a2e",
                                        border_width=1, border_color="#2b2b4a")
        self.result_card.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(self.result_card, text="Scanned Item Details",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#7a7a9e").pack(pady=(15, 0))

        self.result_label = ctk.CTkLabel(self.result_card, text="Waiting for physical scan...",
                                         font=ctk.CTkFont(size=15), text_color="#7a7a9e",
                                         justify="left")
        self.result_label.pack(pady=20, padx=20, expand=True)

        # --- SAĞ PANEL ---
        right = ctk.CTkFrame(content, corner_radius=10, fg_color="#1a1a2e",
                             border_width=1, border_color="#2b2b4a")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(right, text="📋 Live Transaction Logs",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e0e0ff").pack(pady=(15, 5))

        self.history_box = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Courier", size=12),
                                          fg_color="#16162a", text_color="#a8c7fa", wrap="word")
        self.history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.history_box.insert("end", "[SYSTEM] RFID Module Initialized.\n")
        self.history_box.insert("end", "[SYSTEM] Awaiting tags...\n")
        self.history_box.insert("end", "-" * 35 + "\n")
        self.history_box.configure(state="disabled")

        self.entry_rfid.focus()

    def zone_scan(self):
        tag = self.entry_rfid.get()
        if not tag:
            self.status_label.configure(text="🔴 No tag present in zone", text_color="#e74c3c")
            return
        self.status_label.configure(text="🟡 Tag detected, querying DB...", text_color="#f1c40f")
        self.after(300, self.auto_scan)

    def auto_scan(self, event=None):
        tag = self.entry_rfid.get()
        if not tag:
            return
        self.status_label.configure(text="🟡 Processing...", text_color="#f1c40f")
        result = scan_rfid(tag, user=self.current_user)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_box.configure(state="normal")

        if result:
            name, batch, expire, remaining = result
            text = f"📦 Product:\t{name}\n\n🏷️ Batch No:\t{batch}\n\n⏳ Expiry:\t{expire}\n\n📊 Remaining:\t{remaining} units"

            # Stok durumuna göre renk
            if remaining == 0:
                qty_warning = "\n\n🚫 OUT OF STOCK!"
                text += qty_warning
                border_color = "#e74c3c"
                status_text = "🔴 Stock Depleted!"
                status_color = "#e74c3c"
            elif remaining <= 20:
                qty_warning = "\n\n⚠️ LOW STOCK WARNING"
                text += qty_warning
                border_color = "#e67e22"
                status_text = f"🟠 Low Stock Alert ({remaining} left)"
                status_color = "#e67e22"
            else:
                border_color = "#2ecc71"
                status_text = "🟢 Stock Updated Successfully"
                status_color = "#2ecc71"

            self.result_label.configure(text=text, text_color="white",
                                        font=ctk.CTkFont(size=16, weight="bold"))
            self.result_card.configure(border_color=border_color, border_width=2)
            self.status_label.configure(text=status_text, text_color=status_color)
            log_line = f"[{timestamp}] DISPENSED: {tag} -> {name} (Stock: {remaining})\n"
        else:
            text = "⚠️ ERROR:\nUnregistered or Invalid RFID Tag"
            self.result_label.configure(text=text, text_color="#e74c3c",
                                        font=ctk.CTkFont(size=15, weight="bold"))
            self.result_card.configure(border_color="#e74c3c", border_width=2)
            self.status_label.configure(text="🔴 Invalid Tag Alert", text_color="#e74c3c")
            log_line = f"[{timestamp}] WARNING: {tag} -> UNKNOWN TAG\n"

        self.history_box.insert("end", log_line)
        self.history_box.see("end")
        self.history_box.configure(state="disabled")
        self.entry_rfid.delete(0, "end")
        self.after(2000, self.reset_status)

    def reset_status(self):
        self.status_label.configure(text="🟢 Scanner Ready", text_color="#2ecc71")
        self.result_card.configure(border_color="#2b2b4a", border_width=1)
        self.result_label.configure(text="Waiting for physical scan...", text_color="#7a7a9e",
                                    font=ctk.CTkFont(size=15))
