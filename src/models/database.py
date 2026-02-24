import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path="data/inventory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create all tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Brands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brands (
                    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    sku VARCHAR(50) UNIQUE NOT NULL,
                    category_id INTEGER,
                    brand_id INTEGER,
                    description TEXT,
                    stock INTEGER DEFAULT 0,
                    price_normal DECIMAL(10,2) NOT NULL,
                    price_workshop DECIMAL(10,2) NOT NULL,
                    cost_price DECIMAL(10,2) NOT NULL,
                    reorder_level INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (category_id),
                    FOREIGN KEY (brand_id) REFERENCES brands (brand_id)
                )
            ''')
            
            # Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    type VARCHAR(20) DEFAULT 'Normal',
                    contact VARCHAR(500),
                    credit_balance DECIMAL(10,2) DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Suppliers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    contact_person VARCHAR(200),
                    email VARCHAR(200),
                    phone VARCHAR(50),
                    address TEXT,
                    credit_balance DECIMAL(10,2) DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number VARCHAR(50) UNIQUE NOT NULL,
                    customer_id INTEGER,
                    sale_date DATE NOT NULL,
                    payment_method VARCHAR(20) DEFAULT 'cash',
                    subtotal DECIMAL(10,2) NOT NULL,
                    discount DECIMAL(10,2) DEFAULT 0,
                    tax DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    paid_amount DECIMAL(10,2) DEFAULT 0,
                    balance DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'completed',
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Sales items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    discount DECIMAL(10,2) DEFAULT 0,
                    total DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Purchases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number VARCHAR(50) NOT NULL,
                    supplier_id INTEGER,
                    purchase_date DATE NOT NULL,
                    payment_method VARCHAR(20) DEFAULT 'cash',
                    subtotal DECIMAL(10,2) NOT NULL,
                    discount DECIMAL(10,2) DEFAULT 0,
                    tax DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    paid_amount DECIMAL(10,2) DEFAULT 0,
                    balance DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'completed',
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            ''')
            
            # Purchase items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchase_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (purchase_id) REFERENCES purchases (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Users table (optional for login system)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Stock movements table for tracking inventory changes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type VARCHAR(20) NOT NULL,
                    quantity INTEGER NOT NULL,
                    reference_id INTEGER,
                    reference_type VARCHAR(20),
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Payments table for tracking customer and supplier payments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_type VARCHAR(20) NOT NULL,  -- 'customer' or 'supplier'
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_method VARCHAR(20) DEFAULT 'cash',
                    reference_number VARCHAR(50),
                    notes TEXT,
                    payment_date DATE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales (sale_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales (customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases (purchase_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_supplier ON purchases (supplier_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements (product_id)')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results as dictionaries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]
    
    def execute_insert(self, query, params=None):
        """Execute insert query and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query, params=None):
        """Execute update/delete query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount

# Global database instance
db = Database()
