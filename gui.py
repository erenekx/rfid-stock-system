import customtkinter as ctk
import datetime
from rfid_simulator import scan_rfid

# Tema Ayarları (Modern Koyu Tema)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RFIDApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("RFID Stock Management System - Staff Dashboard")
        self.geometry("750x500")
        self.configure(padx=20, pady=20)

        # 2 Sütunlu Grid Sistemi (Sol: Scanner, Sağ: Loglar)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=1)

        # --- Üst Başlık (Header) ---
        self.header_label = ctk.CTkLabel(
            self,
            text="📡 RFID Scan & Stock Movement",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # ==========================================
        # SOL PANEL (Hardware Interface & Results)
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 15))

        # RFID Reader Simülasyon Kartı
        self.reader_card = ctk.CTkFrame(self.left_frame, corner_radius=10)
        self.reader_card.pack(fill="x", pady=(0, 15))

        self.zone_title = ctk.CTkLabel(
            self.reader_card,
            text="Hardware Interface",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.zone_title.pack(pady=(10, 5))

        self.entry_rfid = ctk.CTkEntry(
            self.reader_card,
            placeholder_text="Waiting for EPC tag...",
            width=280,
            height=40,
            font=ctk.CTkFont(size=15),
            justify="center"
        )
        self.entry_rfid.pack(pady=10)
        self.entry_rfid.bind("<Return>", self.auto_scan)

        self.zone_button = ctk.CTkButton(
            self.reader_card,
            text="Simulate Tag Reading",
            height=40,
            command=self.zone_scan,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#2b719e",
            hover_color="#1f538d"
        )
        self.zone_button.pack(pady=(0, 15))

        # Durum Göstergesi (Status)
        self.status_label = ctk.CTkLabel(
            self.left_frame,
            text="🟢 Scanner Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71"  # Zümrüt Yeşili
        )
        self.status_label.pack(pady=5)

        # Okutulan İlaç Sonuç Kartı
        self.result_card = ctk.CTkFrame(self.left_frame, corner_radius=10, fg_color="#242424")
        self.result_card.pack(fill="both", expand=True, pady=10)

        self.result_title = ctk.CTkLabel(
            self.result_card,
            text="Scanned Item Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.result_title.pack(pady=(10, 0))

        self.result_label = ctk.CTkLabel(
            self.result_card,
            text="Waiting for physical scan...",
            font=ctk.CTkFont(size=15),
            justify="left"
        )
        self.result_label.pack(pady=20, padx=20, expand=True)

        # ==========================================
        # SAĞ PANEL (Live Transaction Logs)
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=1, column=1, sticky="nsew")

        self.log_title = ctk.CTkLabel(
            self.right_frame,
            text="📋 Live Transaction Logs",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.log_title.pack(pady=(15, 5))

        self.history_box = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(family="Courier", size=12),
            fg_color="#1e1e1e",
            text_color="#a8c7fa",  # Terminal Mavisi
            wrap="word"
        )
        self.history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Başlangıç Mesajları
        self.history_box.insert("end", "[SYSTEM] RFID Module Initialized.\n")
        self.history_box.insert("end", "[SYSTEM] Awaiting tags...\n")
        self.history_box.insert("end", "-" * 35 + "\n")
        self.history_box.configure(state="disabled")

        self.entry_rfid.focus()

    def zone_scan(self):
        """Butona basılınca okuma simülasyonu tetikler"""
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
        result = scan_rfid(tag)

        # Log için zaman damgası
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_box.configure(state="normal")

        if result:
            name, batch, expire, remaining = result
            # Ekrana Şık Yazdırma Formatı
            text = f"📦 Product:\t{name}\n\n🏷️ Batch No:\t{batch}\n\n⏳ Expiry:\t{expire}\n\n📊 Remaining:\t{remaining} units"
            self.result_label.configure(text=text, text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
            self.result_card.configure(border_color="#2ecc71", border_width=2)  # Başarılı okuma yeşil çerçeve

            self.status_label.configure(text="🟢 Stock Updated Successfully", text_color="#2ecc71")
            log_line = f"[{timestamp}] DISPENSED: {tag} -> {name} (Stock: {remaining})\n"
        else:
            text = "⚠️ ERROR:\nUnregistered or Invalid RFID Tag"
            self.result_label.configure(text=text, text_color="#e74c3c", font=ctk.CTkFont(size=15, weight="bold"))
            self.result_card.configure(border_color="#e74c3c", border_width=2)  # Hatalı okuma kırmızı çerçeve

            self.status_label.configure(text="🔴 Invalid Tag Alert", text_color="#e74c3c")
            log_line = f"[{timestamp}] WARNING: {tag} -> UNKNOWN TAG\n"

        # Log'a ekle ve en alta kaydır
        self.history_box.insert("end", log_line)
        self.history_box.see("end")
        self.history_box.configure(state="disabled")

        # Kutuyu temizle ve 2 saniye sonra ekranı sıfırla
        self.entry_rfid.delete(0, "end")
        self.after(2000, self.reset_status)

    def reset_status(self):
        """Sonuç ekranını beklemeye moduna geri alır"""
        self.status_label.configure(text="🟢 Scanner Ready", text_color="#2ecc71")
        self.result_card.configure(border_width=0)
        self.result_label.configure(text="Waiting for physical scan...", text_color="gray", font=ctk.CTkFont(size=15))