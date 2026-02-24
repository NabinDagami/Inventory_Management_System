import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', tables)

# Check specific table schemas
for table in ['products', 'suppliers', 'purchases', 'sales']:
    try:
        cursor.execute(f'PRAGMA table_info({table})')
        info = cursor.fetchall()
        print(f'{table} table:', info)
    except:
        print(f'{table} table: Does not exist')

conn.close()
