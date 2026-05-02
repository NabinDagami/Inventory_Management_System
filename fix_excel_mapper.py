import codecs

# Read file
with codecs.open('src/utils/excel_mapper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace
old_text = """                        reorder_level = self._to_int(product_data.get('reorder_level', max(stock + 5, 10) if stock < 5 else 10))
                        
                        sku = SKUGenerator.generate_sku(category_id, brand_id)
                        
                        db.execute_insert("""
                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,
                                                price_normal, price_workshop, cost_price, reorder_level, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            product_data['name'], sku, category_id, brand_id, stock, qty_sold,
                            price_normal, workshop_price, cost_price, reorder_level
                        ))"""

new_text = """                        reorder_level = self._to_int(product_data.get('reorder_level', max(stock + 5, 10) if stock < 5 else 10))
                        
                        # Calculate available_stock
                        available_stock = stock - qty_sold
                        
                        sku = SKUGenerator.generate_sku(category_id, brand_id)
                        
                        db.execute_insert("""
                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,
                                                price_normal, price_workshop, cost_price, reorder_level,
                                                available_stock, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            product_data['name'], sku, category_id, brand_id, stock, qty_sold,
                            price_normal, workshop_price, cost_price, reorder_level,
                            available_stock
                        ))"""

if old_text in content:
    content = content.replace(old_text, new_text)
    with codecs.open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed excel_mapper.py')
else:
    print('Text not found, checking for different format...')
    # Try without CRLF
    old_text2 = old_text.replace('\r\n', '\n')
    if old_text2 in content:
        content = content.replace(old_text2, new_text.replace('\r\n', '\n'))
        with codecs.open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed excel_mapper.py (Linux line endings)')
    else:
        print('Still not found')
