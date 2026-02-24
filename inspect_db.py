import sqlite3
import os

db_path = 'data/inventory.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit()

print(f"Checking database at: {os.path.abspath(db_path)}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [table['name'] for table in tables])

# Check specific table schemas and data
for table_name in ['products', 'suppliers', 'purchases', 'purchase_items', 'sales']:
    try:
        cursor.execute(f'PRAGMA table_info({table_name})')
        info = cursor.fetchall()
        print(f'\n{table_name} table schema:')
        for column in info:
            print(f"  {column['name']}: {column['type']}")
        
        # Check data count
        cursor.execute(f'SELECT COUNT(*) as count FROM {table_name}')
        count = cursor.fetchone()['count']
        print(f"{table_name} data count: {count}")
        
        # Show sample data if exists
        if count > 0:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
            sample_data = cursor.fetchall()
            print(f"Sample {table_name} data:")
            for row in sample_data:
                print(f"  {dict(row)}")
                
    except Exception as e:
        print(f'{table_name} table: Error - {e}')

conn.close()
