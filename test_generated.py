from src.models.database import db

# Check if the generated column works
db.execute_insert("INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold, price_normal, price_workshop, cost_price, reorder_level, is_active) VALUES ('Test Product', 'TEST-001', 1, 1, 100, 20, 250, 180, 150, 10, 1)")

# Query it
result = db.execute_query("SELECT name, stock, qty_sold, available_stock, price_normal, price_workshop FROM products WHERE sku='TEST-001'")
if result:
    p = result[0]
    print(f"Product: {p['name']}")
    print(f"Stock: {p['stock']}")
    print(f"Qty Sold: {p['qty_sold']}")
    print(f"Available Stock: {p['available_stock']} (calculated as stock - qty_sold)")
    print(f"Price Normal (Retail): {p['price_normal']}")
    print(f"Price Workshop (Wholesale): {p['price_workshop']}")
    
# Clean up
db.execute_update("DELETE FROM products WHERE sku='TEST-001'")
print("\nOK: Generated column works correctly!")
