import sqlite3

# This creates a database file named store_inventory.db automatically!
conn = sqlite3.connect('store_inventory.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        item_name TEXT,
        city TEXT,
        stock_count INTEGER,
        unit_price REAL
    )
''')

# Insert sample inventory rows
items = [
    ('Burger', 'Karachi', 150, 5.0),
    ('Burger', 'Lahore', 20, 5.0),
    ('Pizza', 'Karachi', 80, 12.0),
    ('Pizza', 'Lahore', 200, 12.0),
    ('Fries', 'Islamabad', 10, 3.0)
]

cursor.executemany('INSERT INTO inventory (item_name, city, stock_count, unit_price) VALUES (?, ?, ?, ?)', items)
conn.commit()
conn.close()
print("Database store_inventory.db created successfully!")