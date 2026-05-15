import customtkinter as ctk
from screens.login_screen import LoginScreen
from screens.admin_dashboard import AdminDashboard
from screens.staff_inventory import StaffInventory
from screens.rfid_scanner import RFIDScannerScreen
from screens.medicine_form import MedicineForm

# Tema Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RFIDStockApp(ctk.CTk):
    """Ana uygulama controller'ı - frame geçişlerini yönetir"""

    def __init__(self):
        super().__init__()

        self.title("RFID Stock Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(padx=20, pady=20)

        # State
        self.current_user = None
        self.current_frame = None

        # Container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Login ekranı ile başla
        self.show_login()

    def _clear_frame(self):
        """Mevcut frame'i temizle"""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        """Login ekranını göster"""
        self._clear_frame()
        self.current_user = None
        self.geometry("1100x700")
        self.title("RFID Stock Management System - Login")
        self.current_frame = LoginScreen(self, on_login_success=self._on_login)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _on_login(self, user):
        """Login başarılı olduğunda çağrılır"""
        self.current_user = user
        user_id, username, role, full_name = user

        if role == "admin":
            self.show_admin_dashboard()
        else:
            self.show_staff_inventory()

    def show_admin_dashboard(self):
        """Admin Dashboard göster"""
        self._clear_frame()
        self.title("RFID Stock Management System - Administrator Dashboard")
        self.current_frame = AdminDashboard(
            self,
            on_logout=self.show_login,
            current_user=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_staff_inventory(self):
        """Staff Inventory Table göster"""
        self._clear_frame()
        self.title("RFID Stock Management System - Staff Dashboard")
        self.current_frame = StaffInventory(
            self,
            on_logout=self.show_login,
            on_switch_scanner=self.show_rfid_scanner,
            on_add_medicine=self.show_medicine_form,
            current_user=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_rfid_scanner(self):
        """RFID Scanner ekranını göster"""
        self._clear_frame()
        self.title("RFID Stock Management System - RFID Scanner")
        self.current_frame = RFIDScannerScreen(
            self,
            on_logout=self.show_login,
            on_switch_inventory=self.show_staff_inventory,
            current_user=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_medicine_form(self):
        """Medicine Registration Form göster"""
        self._clear_frame()
        self.title("RFID Stock Management System - Medicine Registration")
        self.current_frame = MedicineForm(
            self,
            on_back=self.show_staff_inventory
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")
