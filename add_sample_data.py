from src.models.database import db

# Add sample categories
categories = [
    ("Electronics", "Electronic devices and components"),
    ("Hardware", "Hardware tools and equipment"),
    ("Accessories", "Various accessories and parts")
]

for name, desc in categories:
    try:
        db.execute_insert(
            "INSERT INTO categories (category_name, description) VALUES (?, ?)",
            (name, desc)
        )
        print(f"Added category: {name}")
    except Exception as e:
        print(f"Category {name} may already exist: {e}")

# Add sample brands
brands = [
    ("Generic", "Generic brand products"),
    ("Premium", "Premium quality products"),
    ("Budget", "Budget-friendly options")
]

for name, desc in brands:
    try:
        db.execute_insert(
            "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
            (name, desc)
        )
        print(f"Added brand: {name}")
    except Exception as e:
        print(f"Brand {name} may already exist: {e}")

# Add sample suppliers
suppliers = [
    ("ABC Electronics", "John Doe", "john@abc.com", "+1234567890", "123 Main St, City"),
    ("XYZ Hardware", "Jane Smith", "jane@xyz.com", "+0987654321", "456 Oak Ave, Town"),
    ("Global Parts", "Mike Johnson", "mike@global.com", "+1122334455", "789 Pine Rd, Village")
]

for name, contact_person, email, phone, address in suppliers:
    try:
        db.execute_insert(
            "INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES (?, ?, ?, ?, ?)",
            (name, contact_person, email, phone, address)
        )
        print(f"Added supplier: {name}")
    except Exception as e:
        print(f"Supplier {name} may already exist: {e}")

# Add sample products
products = [
    ("PROD001", "Laptop Computer", 1, 1, "High-performance laptop", 10, 999.99, 899.99, 750.00, 5),
    ("PROD002", "USB Cable", 3, 1, "USB-C to USB-A cable", 50, 19.99, 17.99, 8.50, 10),
    ("PROD003", "Wireless Mouse", 1, 2, "Ergonomic wireless mouse", 25, 49.99, 44.99, 25.00, 8),
    ("PROD004", "Screwdriver Set", 2, 1, "Professional screwdriver set", 15, 34.99, 29.99, 18.00, 5),
    ("PROD005", "Monitor Stand", 3, 2, "Adjustable monitor stand", 8, 79.99, 69.99, 35.00, 3)
]

for sku, name, cat_id, brand_id, desc, stock, price_normal, price_workshop, cost_price, reorder in products:
    try:
        db.execute_insert(
            """INSERT INTO products (sku, name, category_id, brand_id, description, stock, 
               price_normal, price_workshop, cost_price, reorder_level) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sku, name, cat_id, brand_id, desc, stock, price_normal, price_workshop, cost_price, reorder)
        )
        print(f"Added product: {name}")
    except Exception as e:
        print(f"Product {name} may already exist: {e}")

print("\nSample data added successfully!")
