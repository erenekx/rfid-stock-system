import sqlite3
import datetime

DB_NAME = "stock.db"


def scan_rfid(tag, user=None):
    """RFID tag okutulduğunda:
    1. Ürün bilgisini getirir
    2. Stok miktarını 1 azaltır
    3. movements tablosuna kullanıcı bilgisiyle kayıt düşer
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ürün bilgisini ve batch_id'yi çek
    cursor.execute("""
    SELECT products.name, batches.batch_code, batches.expire_date, batches.id, batches.quantity
    FROM rfid_items
    JOIN batches ON rfid_items.batch_id = batches.id
    JOIN products ON batches.product_id = products.id
    WHERE rfid_items.rfid_tag = ?
    """, (tag,))

    result = cursor.fetchone()

    if result:
        name, batch_code, expire_date, batch_id, current_qty = result

        # Stok 0'ın altına düşmesin
        new_qty = max(0, current_qty - 1)
        cursor.execute("UPDATE batches SET quantity = ? WHERE id = ?", (new_qty, batch_id))

        # Kullanıcı bilgisi
        user_id = user[0] if user else None
        user_name = user[3] if user else "Unknown"

        # Hareket kaydı oluştur
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO movements (rfid_tag, product_name, action, user_id, user_name, date) VALUES (?, ?, 'DISPENSED', ?, ?, ?)",
            (tag, name, user_id, user_name, now))

        conn.commit()
        conn.close()

        # Kalan stok bilgisini de döndür
        return (name, batch_code, expire_date, new_qty)

    conn.close()
    return None