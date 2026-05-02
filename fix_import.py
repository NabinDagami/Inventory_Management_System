# Read the file
with open('import_excel_to_db.py', 'r') as f:
    content = f.read()

# Replace the problematic function
old_func = '''def import_product_to_db(product, category_id, brand_id):
    """Import a single product to the database"""
        try:
        # Generate SKU using the SKU generator
        sku = SKUGenerator.generate_sku(category_id, brand_id)
        
        # Insert product
        product_id = db.execute_insert("""
            INSERT INTO products (
                name, sku, category_id, brand_id,
                description, stock, qty_sold, 
                price_normal, price_workshop, cost_price,
                reorder_level, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['product_name'],
            sku,
            category_id,
            brand_id,
            product['description'] if 'description' in product else f"Imported from {sheet_name}",
            product['stock'],
            product.get('qty_sold', 0),
            product['normal_price'],
            product['workshop_price'],
            product['cost_price'],
            product['reorder_level'],
            1  # is_active
        ))
        
        return product_id
    except Exception as e:
        print(f"    Error importing product '{product['product_name']}': {e}")
        return None'''

new_func = '''def import_product_to_db(product, category_id, brand_id):
    """Import a single product to the database"""
    try:
        # Generate SKU using the SKU generator
        sku = SKUGenerator.generate_sku(category_id, brand_id)
        
        # Calculate available_stock
        available_stock = product['stock'] - product.get('qty_sold', 0)
        
        # Insert product
        product_id = db.execute_insert("""
            INSERT INTO products (
                name, sku, category_id, brand_id,
                description, stock, qty_sold, available_stock,
                price_normal, price_workshop, cost_price,
                reorder_level, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['product_name'],
            sku,
            category_id,
            brand_id,
            product['description'] if 'description' in product else f"Imported from {sheet_name}",
            product['stock'],
            product.get('qty_sold', 0),
            available_stock,
            product['normal_price'],
            product['workshop_price'],
            product['cost_price'],
            product['reorder_level'],
            1  # is_active
        ))
        
        return product_id
    except Exception as e:
        print(f"    Error importing product '{product['product_name']}': {e}")
        return None'''

content = content.replace(old_func, new_func)

with open('import_excel_to_db.py', 'w') as f:
    f.write(content)

print('Fixed import_excel_to_db.py')
