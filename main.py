import os
import sys

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_database, seed_data
from app import RFIDStockApp

# Veritabanını oluştur ve örnek verilerle doldur
create_database()
seed_data()

# Uygulamayı başlat
app = RFIDStockApp()
app.mainloop()