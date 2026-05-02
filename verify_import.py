"""Verify the imported data"""
import sys
sys.path.insert(0, 'src')

from models.database import db

print("=" * 60)
print("DATABASE VERIFICATION")
print("=" * 60)

# Count products
total_products = db.execute_query('SELECT COUNT(*) as count FROM products')[0]['count']
print(f"\n✓ Total products: {total_products}")

# Count categories
categories = db.execute_query('SELECT * FROM categories')
print(f"✓ Categories: {len(categories)}")

# Count brands
brands = db.execute_query('SELECT * FROM brands')
print(f"✓ Brands: {len(brands)}")

# Sample products
print("\n" + "=" * 60)
print("SAMPLE PRODUCTS")
print("=" * 60)

sample = db.execute_query('''
    SELECT p.sku, p.name, p.stock, p.price_normal, p.cost_price, 
           c.category_name, b.brand_name
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN brands b ON p.brand_id = b.brand_id
    LIMIT 10
''')

for p in sample:
    print(f"\n  SKU: {p['sku']}")
    print(f"  Name: {p['name'][:50]}")
    print(f"  Category: {p['category_name']}")
    print(f"  Brand: {p['brand_name']}")
    print(f"  Stock: {p['stock']} | Price: ₹{p['price_normal']} | Cost: ₹{p['cost_price']}")

print("\n" + "=" * 60)
print("IMPORT VERIFICATION COMPLETE!")
print("=" * 60)
