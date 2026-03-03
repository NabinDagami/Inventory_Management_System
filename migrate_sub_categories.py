"""
Migration script to add sub_category and sub_brand support to existing database
"""
import sqlite3
import os

def migrate_database():
    db_path = "data/inventory.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. New database will be created with the updated schema.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if sub_categories table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sub_categories'")
        if not cursor.fetchone():
            print("Creating sub_categories table...")
            cursor.execute('''
                CREATE TABLE sub_categories (
                    sub_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_category_name VARCHAR(100) NOT NULL,
                    category_id INTEGER NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (category_id),
                    UNIQUE(sub_category_name, category_id)
                )
            ''')
            print("sub_categories table created successfully!")
        else:
            print("sub_categories table already exists.")
        
        # Check if sub_brands table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sub_brands'")
        if not cursor.fetchone():
            print("Creating sub_brands table...")
            cursor.execute('''
                CREATE TABLE sub_brands (
                    sub_brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_brand_name VARCHAR(100) NOT NULL,
                    brand_id INTEGER NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (brand_id) REFERENCES brands (brand_id),
                    UNIQUE(sub_brand_name, brand_id)
                )
            ''')
            print("sub_brands table created successfully!")
        else:
            print("sub_brands table already exists.")
        
        # Check if products table has sub_category_id column
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sub_category_id' not in columns:
            print("Adding sub_category_id column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN sub_category_id INTEGER")
            print("sub_category_id column added!")
        else:
            print("sub_category_id column already exists.")
        
        if 'sub_brand_id' not in columns:
            print("Adding sub_brand_id column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN sub_brand_id INTEGER")
            print("sub_brand_id column added!")
        else:
            print("sub_brand_id column already exists.")
        
        conn.commit()
        print("\nMigration completed successfully!")
        print("You can now use Sub Category and Sub Brand features.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
