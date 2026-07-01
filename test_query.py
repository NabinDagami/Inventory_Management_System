import sys
sys.path.insert(0, 'src')
from models.database import db

rows = db.execute_query("""
    SELECT p.name, c.category_name, b.brand_name
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN brands b ON p.brand_id = b.brand_id
    WHERE p.is_active = 1
    ORDER BY p.name
    LIMIT 10
""")
for r in rows:
    nm = r['name'] or ''
    cn = r['category_name'] or 'NULL'
    bn = r['brand_name'] or 'NULL'
    print(f'{nm:30s} cat={cn:20s} brand={bn}')
print(f'Total active products: {len(rows)}')

# Also show distinct categories and brands
cats = db.execute_query("SELECT DISTINCT c.category_name FROM products p JOIN categories c ON p.category_id = c.category_id WHERE p.is_active = 1 ORDER BY c.category_name")
brands = db.execute_query("SELECT DISTINCT b.brand_name FROM products p JOIN brands b ON p.brand_id = b.brand_id WHERE p.is_active = 1 ORDER BY b.brand_name")
print(f'\nDistinct categories: {[r["category_name"] for r in cats]}')
print(f'Distinct brands: {[r["brand_name"] for r in brands]}')
