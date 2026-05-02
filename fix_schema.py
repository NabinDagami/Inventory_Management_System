from src.models.database import db

# Force re-initialization by checking the schema
db = __import__('src.models.database', fromlist=['Database']).Database('data/inventory.db')

# Check columns
result = db.execute_query('PRAGMA table_info(products)')
print('Current products table columns:')
for col in result:
    print(f'  {col["name"]} ({col["type"]})')

has_available = any(c['name'] == 'available_stock' for c in result)
print(f'\navailable_stock column present: {has_available}')

if not has_available:
    print('\nAdding available_stock column...')
    try:
        db.execute_update('ALTER TABLE products ADD COLUMN available_stock INTEGER DEFAULT 0')
        print('Column added successfully')
        
        # Verify
        result = db.execute_query('PRAGMA table_info(products)')
        has_available = any(c['name'] == 'available_stock' for c in result)
        print(f'Verification: available_stock present = {has_available}')
    except Exception as e:
        print(f'Error: {e}')
        
    # Update existing rows to calculate available_stock
    try:
        rows = db.execute_query('SELECT product_id, stock, qty_sold FROM products')
        updated = 0
        for row in rows:
            available = row['stock'] - row['qty_sold']
            db.execute_update('UPDATE products SET available_stock = ? WHERE product_id = ?',
                            (available, row['product_id']))
            updated += 1
        print(f'Updated {updated} rows with available_stock values')
    except Exception as e:
        print(f'Update error: {e}')
else:
    print('Schema is correct')
