#!/usr/bin/env python3
"""
Sample data population script for Inventory Pro (Updated Schema)
This script adds sample data to demonstrate the application functionality
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import db
from utils.sku_generator import SKUGenerator

def clean_old_data():
    """Clean any existing data to start fresh"""
    tables = ['sale_items', 'purchase_items', 'sales', 'purchases', 'products', 'customers', 'suppliers', 'categories', 'brands']
    
    for table in tables:
        try:
            db.execute_update(f"DELETE FROM {table}")
            print(f"Cleaned {table}")
        except Exception as e:
            print(f"Error cleaning {table}: {e}")

def create_sample_categories():
    """Create sample product categories"""
    categories = [
        ("Electronics", "Electronic devices and components"),
        ("Tools", "Hand tools and power tools"),
        ("Parts", "Mechanical parts and components"),
        ("Accessories", "Various accessories and consumables"),
        ("Hardware", "Nuts, bolts, screws and hardware"),
    ]
    
    for name, description in categories:
        try:
            db.execute_insert(
                "INSERT INTO categories (category_name, description) VALUES (?, ?)",
                (name, description)
            )
            print(f"Added category: {name}")
        except Exception as e:
            print(f"Error adding category {name}: {e}")

def create_sample_brands():
    """Create sample brands"""
    brands = [
        ("Bosch", "Power tools and automotive parts"),
        ("DeWalt", "Professional power tools"),
        ("Sony", "Electronics and components"),
        ("Samsung", "Electronic devices"),
        ("Generic", "Generic brand products"),
        ("OEM", "Original equipment manufacturer"),
    ]
    
    for name, description in brands:
        try:
            db.execute_insert(
                "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
                (name, description)
            )
            print(f"Added brand: {name}")
        except Exception as e:
            print(f"Error adding brand {name}: {e}")

def create_sample_products():
    """Create sample products with auto-generated SKUs"""
    
    # Get category and brand IDs
    categories = db.execute_query("SELECT category_id, category_name FROM categories")
    brands = db.execute_query("SELECT brand_id, brand_name FROM brands")
    
    cat_dict = {cat['category_name']: cat['category_id'] for cat in categories}
    brand_dict = {brand['brand_name']: brand['brand_id'] for brand in brands}
    
    products = [
        # Electronics
        ("LED Strip 5m", cat_dict.get("Electronics"), brand_dict.get("Generic"), 
         "5 meter LED strip with remote", 50, 15.00, 25.00, 22.00, 10),
        ("Arduino Uno", cat_dict.get("Electronics"), brand_dict.get("Generic"),
         "Arduino Uno R3 microcontroller", 25, 12.00, 20.00, 18.00, 5),
        ("Resistor Kit", cat_dict.get("Electronics"), brand_dict.get("Generic"),
         "Assorted resistor kit 100pcs", 30, 8.00, 15.00, 13.00, 5),
        
        # Tools
        ("Cordless Drill", cat_dict.get("Tools"), brand_dict.get("DeWalt"),
         "18V Cordless drill with battery", 15, 85.00, 150.00, 135.00, 3),
        ("Screwdriver Set", cat_dict.get("Tools"), brand_dict.get("Bosch"),
         "Professional screwdriver set 24pcs", 20, 25.00, 45.00, 40.00, 5),
        ("Multimeter", cat_dict.get("Tools"), brand_dict.get("Generic"),
         "Digital multimeter with leads", 12, 18.00, 35.00, 30.00, 3),
        
        # Parts
        ("Ball Bearing 608", cat_dict.get("Parts"), brand_dict.get("OEM"),
         "608 Ball bearing standard", 100, 2.50, 5.00, 4.50, 20),
        ("Motor 12V DC", cat_dict.get("Parts"), brand_dict.get("Generic"),
         "12V DC motor 3000 RPM", 8, 15.00, 28.00, 25.00, 2),
        ("Steel Rod 10mm", cat_dict.get("Parts"), brand_dict.get("Generic"),
         "Steel rod 10mm diameter 1m", 25, 8.00, 15.00, 13.50, 5),
        
        # Hardware
        ("Hex Bolts M6", cat_dict.get("Hardware"), brand_dict.get("Generic"),
         "M6x25 hex bolts stainless steel", 200, 0.50, 1.00, 0.85, 50),
        ("Washers M6", cat_dict.get("Hardware"), brand_dict.get("Generic"),
         "M6 flat washers stainless steel", 500, 0.20, 0.40, 0.35, 100),
    ]
    
    for product_data in products:
        try:
            name, category_id, brand_id, description, stock, cost, price_normal, price_workshop, reorder = product_data
            
            # Generate SKU
            sku = SKUGenerator.generate_sku(category_id, brand_id)
            
            db.execute_insert(
                """INSERT INTO products 
                   (name, sku, category_id, brand_id, description, stock, 
                    price_normal, price_workshop, cost_price, reorder_level) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, sku, category_id, brand_id, description, stock, price_normal, price_workshop, cost, reorder)
            )
            print(f"Added product: {name} (SKU: {sku})")
        except Exception as e:
            print(f"Error adding product {name}: {e}")

def create_sample_customers():
    """Create sample customers"""
    customers = [
        ("John Smith", "Normal", "Phone: 555-0101, Email: john.smith@email.com, Address: 123 Main St, City", 1000.00),
        ("ABC Workshop", "Workshop", "Phone: 555-0102, Email: contact@abcworkshop.com, Address: 456 Industrial Ave", 5000.00),
        ("Jane Doe", "Normal", "Phone: 555-0103, Email: jane.doe@email.com, Address: 789 Oak St, City", 500.00),
        ("Tech Solutions Ltd", "Workshop", "Phone: 555-0104, Email: sales@techsolutions.com, Address: 321 Business Blvd", 3000.00),
        ("Mike Johnson", "Normal", "Phone: 555-0105, Email: mike.j@email.com, Address: 654 Pine St, City", 750.00),
    ]
    
    for customer_data in customers:
        try:
            name, customer_type, contact, credit_balance = customer_data
            db.execute_insert(
                """INSERT INTO customers 
                   (name, type, contact, credit_balance) 
                   VALUES (?, ?, ?, ?)""",
                (name, customer_type, contact, credit_balance)
            )
            print(f"Added customer: {name}")
        except Exception as e:
            print(f"Error adding customer {name}: {e}")

def create_sample_suppliers():
    """Create sample suppliers"""
    suppliers = [
        ("ElectroSupply Co", "Contact: Sarah Wilson, Phone: 555-0201, Email: orders@electrosupply.com", "100 Supply St, Industrial District", 0.0),
        ("Tool Warehouse", "Contact: Bob Martinez, Phone: 555-0202, Email: sales@toolwarehouse.com", "200 Warehouse Ave, Business Park", 0.0),
        ("Parts Direct", "Contact: Lisa Chen, Phone: 555-0203, Email: info@partsdirect.com", "300 Manufacturing Rd, Industrial Zone", 0.0),
        ("Hardware Plus", "Contact: Tom Anderson, Phone: 555-0204, Email: contact@hardwareplus.com", "400 Hardware Blvd, Commercial Area", 0.0),
    ]
    
    for supplier_data in suppliers:
        try:
            name, contact, address, credit_balance = supplier_data
            db.execute_insert(
                """INSERT INTO suppliers 
                   (name, contact, address, credit_balance) 
                   VALUES (?, ?, ?, ?)""",
                (name, contact, address, credit_balance)
            )
            print(f"Added supplier: {name}")
        except Exception as e:
            print(f"Error adding supplier {name}: {e}")

def create_sample_sales():
    """Create sample sales transactions"""
    customers = db.execute_query("SELECT customer_id FROM customers")
    products = db.execute_query("SELECT product_id, price_normal, price_workshop FROM products")
    
    if not customers or not products:
        print("No customers or products found. Skipping sales creation.")
        return
    
    # Create sales for the last 30 days
    for i in range(15):  # Create 15 sample sales
        sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
        customer = random.choice(customers)
        payment_method = random.choice(['cash', 'credit'])
        
        # Generate invoice number
        invoice_number = f"INV-{sale_date.strftime('%Y%m%d')}-{i+1:03d}"
        
        try:
            # Create sale record
            sale_id = db.execute_insert(
                """INSERT INTO sales 
                   (invoice_number, customer_id, sale_date, payment_method, 
                    subtotal, total_amount, paid_amount, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (invoice_number, customer['customer_id'], sale_date.date(), payment_method,
                 0, 0, 0, 'completed')  # Will update totals after adding items
            )
            
            # Add 1-3 random products to the sale
            num_items = random.randint(1, 3)
            subtotal = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                
                # Use normal price (we'll implement customer type pricing later)
                unit_price = product['price_normal']
                total = quantity * unit_price
                subtotal += total
                
                # Add sale item
                db.execute_insert(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, quantity, unit_price, total) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (sale_id, product['product_id'], quantity, unit_price, total)
                )
            
            # Update sale totals
            paid_amount = subtotal if payment_method == 'cash' else random.uniform(0, subtotal)
            balance = subtotal - paid_amount
            
            db.execute_update(
                """UPDATE sales 
                   SET subtotal = ?, total_amount = ?, paid_amount = ?, balance = ?
                   WHERE id = ?""",
                (subtotal, subtotal, paid_amount, balance, sale_id)
            )
            
            print(f"Added sale: {invoice_number} - ${subtotal:.2f}")
            
        except Exception as e:
            print(f"Error creating sale: {e}")

def main():
    """Main function to populate sample data"""
    print("=" * 50)
    print("Populating Sample Data for Inventory Pro (Updated Schema)")
    print("=" * 50)
    
    try:
        print("\n0. Cleaning old data...")
        clean_old_data()
        
        print("\n1. Creating sample categories...")
        create_sample_categories()
        
        print("\n2. Creating sample brands...")
        create_sample_brands()
        
        print("\n3. Creating sample products (with auto-generated SKUs)...")
        create_sample_products()
        
        print("\n4. Creating sample customers...")
        create_sample_customers()
        
        print("\n5. Creating sample suppliers...")
        create_sample_suppliers()
        
        print("\n6. Creating sample sales...")
        create_sample_sales()
        
        print("\n" + "=" * 50)
        print("Sample data creation completed!")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Run the application: python main.py")
        print("2. View the dashboard with real data")
        print("3. Test the sales module with sample products")
        print("4. Experience the full functionality")
        
    except Exception as e:
        print(f"Error populating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
