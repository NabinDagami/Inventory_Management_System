import sqlite3

# Connect to database
conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()

try:
    # Add missing columns to suppliers table
    cursor.execute('ALTER TABLE suppliers ADD COLUMN contact_person VARCHAR(200)')
    print("Added contact_person column")
except sqlite3.OperationalError as e:
    print(f"contact_person column may already exist: {e}")

try:
    cursor.execute('ALTER TABLE suppliers ADD COLUMN email VARCHAR(200)')
    print("Added email column")
except sqlite3.OperationalError as e:
    print(f"email column may already exist: {e}")

try:
    cursor.execute('ALTER TABLE suppliers ADD COLUMN phone VARCHAR(50)')
    print("Added phone column")
except sqlite3.OperationalError as e:
    print(f"phone column may already exist: {e}")

conn.commit()
print("Schema updated successfully!")

# Check the updated schema
cursor.execute('PRAGMA table_info(suppliers)')
schema = cursor.fetchall()
print("Updated suppliers table schema:")
for row in schema:
    print(row)

conn.close()
