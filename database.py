import sqlite3
import hashlib
import os

_APP_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "RFID Stock System")
os.makedirs(_APP_DIR, exist_ok=True)
DB_NAME = os.path.join(_APP_DIR, "stock.db")


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        full_name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        batch_code TEXT,
        expire_date TEXT,
        quantity INTEGER DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rfid_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_tag TEXT UNIQUE,
        batch_id INTEGER,
        status TEXT,
        FOREIGN KEY (batch_id) REFERENCES batches(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_tag TEXT,
        product_name TEXT,
        action TEXT,
        user_id INTEGER,
        user_name TEXT,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings(
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    admin_hash = _hash_password("admin123")
    staff_hash = _hash_password("staff123")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, password_hash, role, full_name) VALUES (1, 'admin', ?, 'admin', 'Dr. Ahmet Yılmaz')",
        (admin_hash,))
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, password_hash, role, full_name) VALUES (2, 'staff', ?, 'staff', 'Nurse Elif Demir')",
        (staff_hash,))

    medicines = [
        (1, 'Parol'),
        (2, 'Aspirin'),
        (3, 'Augmentin'),
        (4, 'İbuprofen'),
        (5, 'Amoxicillin'),
        (6, 'Metformin'),
        (7, 'Ventolin'),
        (8, 'Panadol'),
    ]
    for mid, name in medicines:
        cursor.execute("INSERT OR IGNORE INTO products (id, name) VALUES (?, ?)", (mid, name))

    batches = [
        (1, 1, 'B101', '2027-05', 150),
        (2, 2, 'A55', '2026-11', 85),
        (3, 3, 'AUG-220', '2027-03', 60),
        (4, 4, 'IBU-118', '2026-08', 12),
        (5, 5, 'AMX-300', '2025-12', 0),
        (6, 6, 'MET-410', '2028-01', 200),
        (7, 7, 'VNT-77', '2026-06', 45),
        (8, 8, 'PND-990', '2027-09', 95),
    ]
    for bid, pid, code, exp, qty in batches:
        cursor.execute("INSERT OR IGNORE INTO batches (id, product_id, batch_code, expire_date, quantity) VALUES (?, ?, ?, ?, ?)",
                       (bid, pid, code, exp, qty))

    rfid_items = [
        ('RFID-1001', 1, 'IN_STOCK'),
        ('RFID-1002', 1, 'IN_STOCK'),
        ('RFID-2001', 2, 'IN_STOCK'),
        ('RFID-3001', 3, 'IN_STOCK'),
        ('RFID-4001', 4, 'LOW_STOCK'),
        ('RFID-5001', 5, 'EXPIRED'),
        ('RFID-6001', 6, 'IN_STOCK'),
        ('RFID-7001', 7, 'IN_STOCK'),
        ('RFID-8001', 8, 'IN_STOCK'),
    ]
    for tag, bid, status in rfid_items:
        cursor.execute("INSERT OR IGNORE INTO rfid_items (rfid_tag, batch_id, status) VALUES (?, ?, ?)",
                       (tag, bid, status))

    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('low_stock_threshold', '20')")
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('expiry_warning_days', '90')")

    conn.commit()
    conn.close()


def authenticate_user(username, password):
    """Returns (id, username, role, full_name) on success, None otherwise."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pw_hash = _hash_password(password)
    cursor.execute(
        "SELECT id, username, role, full_name FROM users WHERE username = ? AND password_hash = ?",
        (username, pw_hash))
    user = cursor.fetchone()
    conn.close()
    return user


def username_exists(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_user(username, password, role, full_name):
    """Returns True on success, False if username is already taken."""
    if username_exists(username):
        return False
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pw_hash = _hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
        (username, pw_hash, role, full_name))
    conn.commit()
    conn.close()
    return True


def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_user_password(user_id, new_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pw_hash = _hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def log_movement(rfid_tag, product_name, action, user=None):
    import datetime
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user_id = user[0] if user else None
    user_name = user[3] if user else "System"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO movements (rfid_tag, product_name, action, user_id, user_name, date) VALUES (?, ?, ?, ?, ?, ?)",
        (rfid_tag, product_name, action, user_id, user_name, now))
    conn.commit()
    conn.close()


def get_all_inventory():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.id,
            p.name,
            b.batch_code,
            b.quantity,
            b.expire_date,
            CASE
                WHEN b.expire_date < strftime('%Y-%m', 'now') THEN 'Expired'
                WHEN b.quantity <= 20 THEN 'Low Stock'
                ELSE 'In Stock'
            END as status
        FROM products p
        JOIN batches b ON p.id = b.product_id
        ORDER BY p.name
    """)
    inventory = cursor.fetchall()
    conn.close()
    return inventory


def get_system_settings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings")
    settings = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return settings


def update_system_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


def add_medicine(name, batch_code, expire_date, quantity, rfid_tag):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name) VALUES (?)", (name,))
    product_id = cursor.lastrowid
    cursor.execute("INSERT INTO batches (product_id, batch_code, expire_date, quantity) VALUES (?, ?, ?, ?)",
                   (product_id, batch_code, expire_date, quantity))
    batch_id = cursor.lastrowid
    if rfid_tag:
        cursor.execute("INSERT INTO rfid_items (rfid_tag, batch_id, status) VALUES (?, ?, 'IN_STOCK')",
                       (rfid_tag, batch_id))
    conn.commit()
    conn.close()
    return product_id


def get_inventory_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rfid_items")
    total_rfid = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM batches WHERE quantity <= 20 AND quantity > 0")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM batches WHERE expire_date < strftime('%Y-%m', 'now')")
    expired = cursor.fetchone()[0]

    conn.close()
    return {
        'total_products': total_products,
        'total_rfid': total_rfid,
        'low_stock_alerts': low_stock,
        'expired_items': expired
    }


def delete_medicine(product_id):
    """Deletes a product and all related batches, rfid_items and movements."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM batches WHERE product_id = ?", (product_id,))
    batch_ids = [row[0] for row in cursor.fetchall()]

    for bid in batch_ids:
        cursor.execute("SELECT rfid_tag FROM rfid_items WHERE batch_id = ?", (bid,))
        tags = [row[0] for row in cursor.fetchall()]
        for tag in tags:
            cursor.execute("DELETE FROM movements WHERE rfid_tag = ?", (tag,))
        cursor.execute("DELETE FROM rfid_items WHERE batch_id = ?", (bid,))

    cursor.execute("DELETE FROM batches WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()


def get_medicine_details(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, b.batch_code, b.quantity, b.expire_date, b.id as batch_id
        FROM products p
        JOIN batches b ON p.id = b.product_id
        WHERE p.id = ?
    """, (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_medicine(product_id, name, batch_code, expire_date, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ? WHERE id = ?", (name, product_id))
    cursor.execute("""
        UPDATE batches SET batch_code = ?, expire_date = ?, quantity = ?
        WHERE product_id = ?
    """, (batch_code, expire_date, quantity, product_id))
    conn.commit()
    conn.close()


def get_all_movements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, rfid_tag, product_name, action, user_name, date
        FROM movements
        ORDER BY id DESC
        LIMIT 50
    """)
    movements = cursor.fetchall()
    conn.close()
    return movements