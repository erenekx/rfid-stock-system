import sqlite3
import datetime
from database import DB_NAME


def scan_rfid(tag, user=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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

        new_qty = max(0, current_qty - 1)
        cursor.execute("UPDATE batches SET quantity = ? WHERE id = ?", (new_qty, batch_id))

        user_id = user[0] if user else None
        user_name = user[3] if user else "Unknown"

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO movements (rfid_tag, product_name, action, user_id, user_name, date) VALUES (?, ?, 'DISPENSED', ?, ?, ?)",
            (tag, name, user_id, user_name, now))

        conn.commit()
        conn.close()
        return (name, batch_code, expire_date, new_qty)

    conn.close()
    return None


def return_rfid(tag, user=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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

        new_qty = current_qty + 1
        cursor.execute("UPDATE batches SET quantity = ? WHERE id = ?", (new_qty, batch_id))

        user_id = user[0] if user else None
        user_name = user[3] if user else "Unknown"

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO movements (rfid_tag, product_name, action, user_id, user_name, date) VALUES (?, ?, 'RETURNED', ?, ?, ?)",
            (tag, name, user_id, user_name, now))

        conn.commit()
        conn.close()
        return (name, batch_code, expire_date, new_qty)

    conn.close()
    return None