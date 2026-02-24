#!/usr/bin/env python3
"""
Sample data population script for Inventory Pro
This script adds sample data to demonstrate the application functionality
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import db

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
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
            print(f"Added category: {name}")
        except:
            print(f"Category {name} already exists")

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
                "INSERT INTO brands (name, description) VALUES (?, ?)",
                (name, description)
            )
            print(f"Added brand: {name}")
        except:
            print(f"Brand {name} already exists")

def create_sample_products():
    """Create sample products"""
    
    # Get category and brand IDs
    categories = db.execute_query("SELECT id, name FROM categories")
    brands = db.execute_query("SELECT id, name FROM brands")
    
    cat_dict = {cat['name']: cat['id'] for cat in categories}
    brand_dict = {brand['name']: brand['id'] for brand in brands}
    
    products = [
        # Electronics
        ("LED Strip 5m", "LED-001", cat_dict.get("Electronics"), brand_dict.get("Generic"), 
         "5 meter LED strip with remote", 15.00, 25.00, 22.00, 50, 10, "pcs"),
        ("Arduino Uno", "ARD-001", cat_dict.get("Electronics"), brand_dict.get("Generic"),
         "Arduino Uno R3 microcontroller", 12.00, 20.00, 18.00, 25, 5, "pcs"),
        ("Resistor Kit", "RES-001", cat_dict.get("Electronics"), brand_dict.get("Generic"),
         "Assorted resistor kit 100pcs", 8.00, 15.00, 13.00, 30, 5, "kit"),
        
        # Tools
        ("Cordless Drill", "DRL-001", cat_dict.get("Tools"), brand_dict.get("DeWalt"),
         "18V Cordless drill with battery", 85.00, 150.00, 135.00, 15, 3, "pcs"),
        ("Screwdriver Set", "SCR-001", cat_dict.get("Tools"), brand_dict.get("Bosch"),
         "Professional screwdriver set 24pcs", 25.00, 45.00, 40.00, 20, 5, "set"),
        ("Multimeter", "MUL-001", cat_dict.get("Tools"), brand_dict.get("Generic"),
         "Digital multimeter with leads", 18.00, 35.00, 30.00, 12, 3, "pcs"),
        
        # Parts
        ("Ball Bearing 608", "BRG-001", cat_dict.get("Parts"), brand_dict.get("OEM"),
         "608 Ball bearing standard", 2.50, 5.00, 4.50, 100, 20, "pcs"),
        ("Motor 12V DC", "MOT-001", cat_dict.get("Parts"), brand_dict.get("Generic"),
         "12V DC motor 3000 RPM", 15.00, 28.00, 25.00, 8, 2, "pcs"),
        ("Steel Rod 10mm", "ROD-001", cat_dict.get("Parts"), brand_dict.get("Generic"),
         "Steel rod 10mm diameter 1m", 8.00, 15.00, 13.50, 25, 5, "pcs"),
        
        # Hardware
        ("Hex Bolts M6", "HEX-001", cat_dict.get("Hardware"), brand_dict.get("Generic"),
         "M6x25 hex bolts stainless steel", 0.50, 1.00, 0.85, 200, 50, "pcs"),
        ("Washers M6", "WSH-001", cat_dict.get("Hardware"), brand_dict.get("Generic"),
         "M6 flat washers stainless steel", 0.20, 0.40, 0.35, 500, 100, "pcs"),
    ]
    
    for product_data in products:
        try:
            name, code, category_id, brand_id, description, cost, selling, workshop, stock, min_stock, unit = product_data
            db.execute_insert(
                """INSERT INTO products 
                   (name, code, category_id, brand_id, description, cost_price, 
                    selling_price, workshop_price, stock_quantity, min_stock_level, unit) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, code, category_id, brand_id, description, cost, selling, workshop, stock, min_stock, unit)
            )
            print(f"Added product: {name}")
        except Exception as e:
            print(f"Product {name} already exists or error: {e}")

def create_sample_customers():
    """Create sample customers"""
    customers = [
        ("John Smith", "Normal", "555-0101", "john.smith@email.com", "123 Main St, City", 1000.00),
        ("ABC Workshop", "Workshop", "555-0102", "contact@abcworkshop.com", "456 Industrial Ave", 5000.00),
        ("Jane Doe", "Normal", "555-0103", "jane.doe@email.com", "789 Oak St, City", 500.00),
        ("Tech Solutions Ltd", "Workshop", "555-0104", "sales@techsolutions.com", "321 Business Blvd", 3000.00),
        ("Mike Johnson", "Normal", "555-0105", "mike.j@email.com", "654 Pine St, City", 750.00),
    ]
    
    for customer_data in customers:
        try:
            name, customer_type, phone, email, address, credit_limit = customer_data
            db.execute_insert(
                """INSERT INTO customers 
                   (name, customer_type, phone, email, address, credit_limit) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, customer_type, phone, email, address, credit_limit)
            )
            print(f"Added customer: {name}")
        except:
            print(f"Customer {name} already exists")

def create_sample_suppliers():
    """Create sample suppliers"""
    suppliers = [
        ("ElectroSupply Co", "Sarah Wilson", "555-0201", "orders@electrosupply.com", "100 Supply St, Industrial District"),
        ("Tool Warehouse", "Bob Martinez", "555-0202", "sales@toolwarehouse.com", "200 Warehouse Ave, Business Park"),
        ("Parts Direct", "Lisa Chen", "555-0203", "info@partsdirect.com", "300 Manufacturing Rd, Industrial Zone"),
        ("Hardware Plus", "Tom Anderson", "555-0204", "contact@hardwareplus.com", "400 Hardware Blvd, Commercial Area"),
    ]
    
    for supplier_data in suppliers:
        try:
            name, contact_person, phone, email, address = supplier_data
            db.execute_insert(
                """INSERT INTO suppliers 
                   (name, contact_person, phone, email, address) 
                   VALUES (?, ?, ?, ?, ?)""",
                (name, contact_person, phone, email, address)
            )
            print(f"Added supplier: {name}")
        except:
            print(f"Supplier {name} already exists")

def create_sample_sales():
    """Create sample sales transactions"""
    customers = db.execute_query("SELECT id FROM customers")
    products = db.execute_query("SELECT id, selling_price, workshop_price FROM products")
    
    if not customers or not products:
        print("No customers or products found. Skipping sales creation.")
        return
    
    # Create sales for the last 30 days
    for i in range(20):  # Create 20 sample sales
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
                (invoice_number, customer['id'], sale_date.date(), payment_method,
                 0, 0, 0, 'completed')  # Will update totals after adding items
            )
            
            # Add 1-3 random products to the sale
            num_items = random.randint(1, 3)
            subtotal = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                
                # Use selling price or workshop price based on customer type
                customer_data = db.execute_query("SELECT customer_type FROM customers WHERE id = ?", (customer['id'],))
                if customer_data and customer_data[0]['customer_type'] == 'Workshop':
                    unit_price = product['workshop_price']
                else:
                    unit_price = product['selling_price']
                
                total = quantity * unit_price
                subtotal += total
                
                # Add sale item
                db.execute_insert(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, quantity, unit_price, total) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (sale_id, product['id'], quantity, unit_price, total)
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
    print("Populating Sample Data for Inventory Pro")
    print("=" * 50)
    
    try:
        print("\n1. Creating sample categories...")
        create_sample_categories()
        
        print("\n2. Creating sample brands...")
        create_sample_brands()
        
        print("\n3. Creating sample products...")
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
        print("3. Explore all modules with sample data")
        print("4. Test all features and functionality")
        
    except Exception as e:
        print(f"Error populating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
