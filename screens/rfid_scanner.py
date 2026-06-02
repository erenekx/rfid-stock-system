import customtkinter as ctk
import theme as T
from rfid_simulator import scan_rfid, return_rfid
import datetime


class RFIDScannerScreen(ctk.CTkFrame):

    def __init__(self, parent, on_logout, on_switch_inventory, current_user=None):
        super().__init__(parent, fg_color=T.BG_PRIMARY)
        self.on_logout = on_logout
        self.on_switch_inventory = on_switch_inventory
        self.current_user = current_user
        self.scan_mode = "DISPENSE"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_navbar()
        self._build_tabs()
        self._build_scanner()

    # ─── Navigation Bar ───────────────────────────────────────────────────────
    def _build_navbar(self):
        nav = T.navbar(self)
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            nav, text="RFID Scanner",
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

    # ─── Tab Bar ──────────────────────────────────────────────────────────────
    def _build_tabs(self):
        seg = ctk.CTkFrame(
            self, fg_color=T.BG_SECONDARY,
            corner_radius=T.RADIUS_MD,
            border_width=1, border_color=T.BORDER
        )
        seg.grid(row=1, column=0, sticky="w", pady=(0, 12))

        T.secondary_button(
            seg, text="Inventory", height=34, width=120,
            command=self.on_switch_inventory
        ).pack(side="left", padx=6, pady=6)

        ctk.CTkButton(
            seg, text="RFID Scanner", height=34, width=130,
            corner_radius=T.RADIUS_SM,
            fg_color=T.BLUE, hover_color=T.BLUE_HOVER,
            text_color=T.TEXT_PRIMARY, font=T.callout_bold()
        ).pack(side="left", pady=6)

    # ─── Main Content ─────────────────────────────────────────────────────────
    def _build_scanner(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=55)
        content.grid_columnconfigure(1, weight=40)
        content.grid_rowconfigure(0, weight=1)

        self._build_left(content)
        self._build_right(content)

    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)

        # ── Hardware Interface Card ────────────────────────────────────────
        reader = T.card(left)
        reader.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(
            reader, text="Hardware Interface",
            font=T.subheadline(), text_color=T.TEXT_PRIMARY
        ).pack(pady=(20, 4), padx=20, anchor="w")

        ctk.CTkLabel(
            reader, text="Enter EPC tag or use simulate button",
            font=T.footnote(), text_color=T.TEXT_SECONDARY
        ).pack(anchor="w", padx=20, pady=(0, 16))

        # Mode selector
        mode_frame = ctk.CTkFrame(
            reader, fg_color=T.BG_TERTIARY,
            corner_radius=T.RADIUS_MD
        )
        mode_frame.pack(fill="x", padx=20, pady=(0, 14))

        ctk.CTkLabel(
            mode_frame, text="Mode",
            font=T.caption(), text_color=T.TEXT_SECONDARY
        ).pack(anchor="w", padx=12, pady=(8, 4))

        btn_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(0, 8))

        self.dispense_btn = ctk.CTkButton(
            btn_row, text="Dispense", width=0, height=34,
            corner_radius=T.RADIUS_SM,
            fg_color=T.ORANGE, hover_color=T.ORANGE_HOVER,
            text_color=T.TEXT_PRIMARY, font=T.callout_bold(),
            command=self._set_dispense_mode
        )
        self.dispense_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.return_btn = ctk.CTkButton(
            btn_row, text="Return", width=0, height=34,
            corner_radius=T.RADIUS_SM,
            fg_color=T.BG_QUATERNARY, hover_color=T.BG_HOVER,
            text_color=T.TEXT_SECONDARY, font=T.callout_bold(),
            command=self._set_return_mode
        )
        self.return_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Tag input
        self.entry_rfid = T.text_input(
            reader, placeholder="Scan or type EPC tag...",
            height=44, justify="center"
        )
        self.entry_rfid.pack(fill="x", padx=20, pady=(0, 10))
        self.entry_rfid.bind("<Return>", self.auto_scan)

        self.scan_btn = T.primary_button(
            reader, text="Simulate Dispense",
            height=42,
            fg_color=T.ORANGE, hover_color=T.ORANGE_HOVER,
            command=self.zone_scan
        )
        self.scan_btn.pack(fill="x", padx=20, pady=(0, 20))

        # ── Status Indicator ──────────────────────────────────────────────
        status_row = ctk.CTkFrame(left, fg_color="transparent")
        status_row.grid(row=0, column=0, sticky="se", padx=4)

        self.status_dot = ctk.CTkFrame(
            reader, width=8, height=8,
            corner_radius=4, fg_color=T.GREEN
        )

        self.status_label = ctk.CTkLabel(
            left, text="Scanner Ready  —  Dispense Mode",
            font=T.footnote(), text_color=T.GREEN
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=4)
        left.grid_rowconfigure(1, weight=0)
        left.grid_rowconfigure(2, weight=1)

        # ── Result Card ────────────────────────────────────────────────────
        self.result_card = T.card(left)
        self.result_card.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.result_card, text="Scanned Item",
            font=T.subheadline(), text_color=T.TEXT_PRIMARY
        ).pack(pady=(20, 4), padx=20, anchor="w")

        T.separator(self.result_card).pack(fill="x", padx=20, pady=(0, 16))

        self.result_label = ctk.CTkLabel(
            self.result_card,
            text="Awaiting scan...",
            font=T.callout(), text_color=T.TEXT_SECONDARY,
            justify="left"
        )
        self.result_label.pack(pady=0, padx=20, anchor="w", expand=True)

    def _build_right(self, parent):
        right = T.card(parent)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(right, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            hdr, text="Transaction Log",
            font=T.subheadline(), text_color=T.TEXT_PRIMARY
        ).pack(side="left")

        T.separator(right).pack(fill="x", padx=20, pady=12)

        self.history_box = ctk.CTkTextbox(
            right,
            font=ctk.CTkFont(family="SF Mono", size=11),
            fg_color=T.BG_TERTIARY,
            text_color=T.TEAL,
            corner_radius=T.RADIUS_SM,
            wrap="word",
            border_width=0
        )
        self.history_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.history_box.insert("end", "[SYS] RFID module initialized\n")
        self.history_box.insert("end", "[SYS] Awaiting tags...\n")
        self.history_box.insert("end", "─" * 32 + "\n")
        self.history_box.configure(state="disabled")

        self.entry_rfid.focus()

    # ─── Mode Switching ───────────────────────────────────────────────────────
    def _set_dispense_mode(self):
        self.scan_mode = "DISPENSE"
        self.dispense_btn.configure(fg_color=T.ORANGE, hover_color=T.ORANGE_HOVER, text_color=T.TEXT_PRIMARY)
        self.return_btn.configure(fg_color=T.BG_QUATERNARY, hover_color=T.BG_HOVER, text_color=T.TEXT_SECONDARY)
        self.scan_btn.configure(text="Simulate Dispense", fg_color=T.ORANGE, hover_color=T.ORANGE_HOVER)
        self.status_label.configure(text="Scanner Ready  —  Dispense Mode", text_color=T.GREEN)
        self.result_card.configure(border_color=T.BORDER)
        self.result_label.configure(text="Awaiting scan...", text_color=T.TEXT_SECONDARY, font=T.callout())

    def _set_return_mode(self):
        self.scan_mode = "RETURN"
        self.return_btn.configure(fg_color=T.GREEN, hover_color=T.GREEN_HOVER, text_color=T.TEXT_PRIMARY)
        self.dispense_btn.configure(fg_color=T.BG_QUATERNARY, hover_color=T.BG_HOVER, text_color=T.TEXT_SECONDARY)
        self.scan_btn.configure(text="Simulate Return", fg_color=T.GREEN, hover_color=T.GREEN_HOVER)
        self.status_label.configure(text="Scanner Ready  —  Return Mode", text_color=T.BLUE)
        self.result_card.configure(border_color=T.BORDER)
        self.result_label.configure(text="Awaiting scan...", text_color=T.TEXT_SECONDARY, font=T.callout())

    # ─── Scan Logic ───────────────────────────────────────────────────────────
    def zone_scan(self):
        tag = self.entry_rfid.get()
        if not tag:
            self.status_label.configure(text="No tag in zone.", text_color=T.RED)
            return
        self.status_label.configure(text="Tag detected — querying...", text_color=T.ORANGE)
        self.after(300, self.auto_scan)

    def auto_scan(self, event=None):
        tag = self.entry_rfid.get()
        if not tag:
            return
        self.status_label.configure(text="Processing...", text_color=T.ORANGE)

        if self.scan_mode == "RETURN":
            result = return_rfid(tag, user=self.current_user)
        else:
            result = scan_rfid(tag, user=self.current_user)

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_box.configure(state="normal")

        if result:
            name, batch, expire, remaining = result

            if self.scan_mode == "RETURN":
                detail = (
                    f"Product      {name}\n"
                    f"Batch        {batch}\n"
                    f"Expiry       {expire}\n"
                    f"New Stock    {remaining} units\n\n"
                    f"Returned to stock"
                )
                border_col = T.GREEN
                status_txt = f"Returned  —  {remaining} in stock"
                status_col = T.GREEN
                log = f"[{ts}] RETURN   {tag}  {name}  stock:{remaining}\n"
            else:
                detail = (
                    f"Product      {name}\n"
                    f"Batch        {batch}\n"
                    f"Expiry       {expire}\n"
                    f"Remaining    {remaining} units"
                )
                if remaining == 0:
                    detail += "\n\nOut of stock"
                    border_col = T.RED
                    status_txt = "Stock depleted"
                    status_col = T.RED
                elif remaining <= 20:
                    detail += "\n\nLow stock warning"
                    border_col = T.ORANGE
                    status_txt = f"Low stock  —  {remaining} left"
                    status_col = T.ORANGE
                else:
                    border_col = T.GREEN
                    status_txt = "Dispensed successfully"
                    status_col = T.GREEN
                log = f"[{ts}] DISPENSE {tag}  {name}  stock:{remaining}\n"

            self.result_label.configure(
                text=detail, text_color=T.TEXT_PRIMARY,
                font=ctk.CTkFont(family=T.FONT_FAMILY, size=13)
            )
            self.result_card.configure(border_color=border_col, border_width=2)
            self.status_label.configure(text=status_txt, text_color=status_col)
        else:
            self.result_label.configure(
                text="Unregistered or invalid RFID tag.",
                text_color=T.RED, font=T.callout()
            )
            self.result_card.configure(border_color=T.RED, border_width=2)
            self.status_label.configure(text="Invalid tag", text_color=T.RED)
            log = f"[{ts}] WARNING  {tag}  UNKNOWN\n"

        self.history_box.insert("end", log)
        self.history_box.see("end")
        self.history_box.configure(state="disabled")
        self.entry_rfid.delete(0, "end")
        self.after(2000, self.reset_status)

    def reset_status(self):
        if self.scan_mode == "RETURN":
            self.status_label.configure(text="Scanner Ready  —  Return Mode", text_color=T.BLUE)
        else:
            self.status_label.configure(text="Scanner Ready  —  Dispense Mode", text_color=T.GREEN)
        self.result_card.configure(border_color=T.BORDER, border_width=1)
        self.result_label.configure(
            text="Awaiting scan...", text_color=T.TEXT_SECONDARY, font=T.callout()
        )
