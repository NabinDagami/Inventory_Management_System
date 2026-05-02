from src.models.database import db

# Check products
result = db.execute_query('SELECT name, stock, qty_sold, price_normal, price_workshop FROM products LIMIT 5')
for p in result:
    print(f"{p['name']}: stock={p['stock']}, sold={p['qty_sold']}, normal={p['price_normal']}, workshop={p['price_workshop']}")

total = db.execute_query('SELECT COUNT(*) as count FROM products')
print(f"\nTotal products: {total[0]['count']}")

# Check categories
cats = db.execute_query('SELECT COUNT(*) as count FROM categories')
print(f"Total categories: {cats[0]['count']}")

# Check brands  
brands = db.execute_query('SELECT COUNT(*) as count FROM brands')
print(f"Total brands: {brands[0]['count']}")
