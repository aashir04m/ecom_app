import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        logged_in BOOLEAN DEFAULT 0  -- New column for login status (0 = not logged in)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        image_path TEXT,
        shopper_id INTEGER,
        FOREIGN KEY (shopper_id) REFERENCES users(id)
    )
''')

cursor.execute("INSERT INTO users (username, password, role, logged_in) VALUES (?, ?, ?, ?)",
               ('shopper', 'admin', 'Shopper', 0))
cursor.execute("INSERT INTO users (username, password, role, logged_in) VALUES (?, ?, ?, ?)",
               ('client', 'admin', 'Client', 0))

conn.commit()
conn.close()
