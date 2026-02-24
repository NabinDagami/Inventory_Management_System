from src.models.database import db

# Add sample customers
customers = [
    ("John Smith", "Normal", "Phone: +1234567890\nEmail: john@email.com", 0.00, 1),
    ("Auto Repair Shop", "Workshop", "Phone: +9876543210\nEmail: info@autorepair.com\nAddress: 123 Mechanic St", 150.00, 1),
    ("Mary Johnson", "Normal", "Phone: +5555551234\nEmail: mary.johnson@example.com", -25.50, 1),
    ("Tech Solutions Inc", "Workshop", "Phone: +1111222333\nEmail: contact@techsolutions.com", 75.25, 1),
    ("Bob Wilson", "Normal", "Phone: +9999888777", 0.00, 0)  # Inactive customer
]

for name, customer_type, contact, credit_balance, is_active in customers:
    try:
        db.execute_insert(
            "INSERT INTO customers (name, type, contact, credit_balance, is_active) VALUES (?, ?, ?, ?, ?)",
            (name, customer_type, contact, credit_balance, is_active)
        )
        print(f"Added customer: {name}")
    except Exception as e:
        print(f"Customer {name} may already exist: {e}")

print("\nSample customers added successfully!")
