# Read file
with open('src/utils/excel_mapper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the INSERT statement and replace it
import re

# Pattern to find the INSERT block
pattern = r"(reorder_level = self\._to_int\(product_data\.get\('reorder_level'.*?\n)(\s+sku = SKUGenerator\.generate_sku\(category_id, brand_id\)\s*\n\s*\n\s*db\.execute_insert\(\"\"\"\s*\n\s*INSERT INTO products \(name, sku, category_id, brand_id, stock, qty_sold,\s*\n\s*price_normal, price_workshop, cost_price, reorder_level, is_active\)\s*\n\s*VALUES \(\?, \?, \?, \?, \?, \?, \?, \?, \?, \?, 1\)\s*\n\s*\"\"\",\s*\(\s*\n\s*product_data\['name'\], sku, category_id, brand_id, stock, qty_sold,\s*\n\s*price_normal, workshop_price, cost_price, reorder_level\s*\n\s*\)\s*\n)"

# Check if pattern exists
if re.search(pattern, content, re.DOTALL):
    # Replacement with available_stock
    replacement = r"""\1
                        # Calculate available_stock
                        available_stock = stock - qty_sold
                        
\2"""
    
    # Now replace the INSERT part within the matched content
    insert_pattern = r"(INSERT INTO products \(name, sku, category_id, brand_id, stock, qty_sold,\s*\n\s*)price_normal, price_workshop, cost_price, reorder_level, is_active\)"
    insert_replacement = r"\1price_normal, price_workshop, cost_price, reorder_level,\n                                                available_stock, is_active)"
    
    values_pattern = r"(VALUES \(\?, \?, \?, \?, \?, \?, \?, \?, \?, \?, )1\)"
    values_replacement = r"\1?, 1)"
    
    params_pattern = r"(price_normal, workshop_price, cost_price, reorder_level)\s*\n"
    params_replacement = r"\1,\n                            available_stock\n"
    
    # Apply replacements to the replacement text
    replacement = re.sub(insert_pattern, insert_replacement, replacement)
    replacement = re.sub(values_pattern, values_replacement, replacement)
    replacement = re.sub(params_pattern, params_replacement, replacement)
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write back
    with open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('Fixed excel_mapper.py successfully')
else:
    print('Pattern not found, trying simpler approach...')
"