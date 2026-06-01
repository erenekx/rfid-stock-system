import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_database, seed_data
from app import RFIDStockApp

create_database()
seed_data()

app = RFIDStockApp()
app.mainloop()