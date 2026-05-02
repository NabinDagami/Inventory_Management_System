# Read the file
with open('src/utils/excel_mapper.py', 'rb') as f:
    content = f.read()

# Decode
content_str = content.decode('utf-8')

# Replace the specific section
old_section = '''                        reorder_level = self._to_int(product_data.get('reorder_level', max(stock + 5, 10) if stock < 5 else 10))
                        
                        sku = SKUGenerator.generate_sku(category_id, brand_id)
                        
                        db.execute_insert("""
                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,
                                                price_normal, price_workshop, cost_price, reorder_level, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            product_data['name'], sku, category_id, brand_id, stock, qty_sold,
                            price_normal, workshop_price, cost_price, reorder_level
                        ))'''

new_section = '''                        reorder_level = self._to_int(product_data.get('reorder_level', max(stock + 5, 10) if stock < 5 else 10))
                        
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
                        ))'''

if old_section in content_str:
    content_str = content_str.replace(old_section, new_section)
    
    # Write back
    with open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
        f.write(content_str)
    
    print('Successfully fixed excel_mapper.py')
else:
    print('Section not found exactly, trying with line ending variations...')
    
    # Try with \r\n
    old_section_crlf = old_section.replace('\n', '\r\n')
    if old_section_crlf in content_str:
        content_str = content_str.replace(old_section_crlf, new_section.replace('\n', '\r\n'))
        with open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
            f.write(content_str)
        print('Fixed with CRLF line endings')
    else:
        print('Still not found')
"