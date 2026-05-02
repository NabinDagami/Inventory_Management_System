# Read file
with open('src/utils/excel_mapper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the INSERT statement and update it
for i in range(len(lines)):
    if 'INSERT INTO products' in lines[i] and i > 910:
        # Check if we need to add available_stock
        if 'available_stock' not in lines[i]:
            # Modify the INSERT line
            lines[i] = '                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,\n'
            # Add the next line
            if i+1 < len(lines) and 'price_normal' in lines[i+1]:
                lines[i+1] = '                                                price_normal, price_workshop, cost_price, reorder_level,\n'
                # Add new line after that
                lines.insert(i+2, '                                                available_stock, is_active)\n')
                # Remove old is_active line if it exists
                if i+3 < len(lines) and is_active' in lines[i+3]:
                    lines.pop(i+3)
            
            # Now update the VALUES part
            for j in range(i, min(i+10, len(lines))):
                if 'VALUES' in lines[j] and '?' in lines[j]:
                    # Update the VALUES line
                    lines[j] = '                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)\n'
                    # Update the parameter line
                    for k in range(j, min(j+5, len(lines))):
                        if 'price_normal' in lines[k]:
                            lines[k] = '                            price_normal, workshop_price, cost_price, reorder_level,\n'
                            # Add new parameter line
                            lines.insert(k+1, '                            available_stock\n')
                            break
                    break
            
            # Also add the available_stock calculation before the INSERT
            for j in range(i-10, i):
                if j > 0 and 'reorder_level = self._to_int' in lines[j]:
                    # Add after reorder_level calculation
                    lines.insert(j+1, '                        \n')
                    lines.insert(j+2, '                        # Calculate available_stock\n')
                    lines.insert(j+3, '                        available_stock = stock - qty_sold\n')
                    lines.insert(j+4, '                        \n')
                    break
            
            print('Found and updated INSERT statement at line', i+1)
            break

# Write back
with open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Updated excel_mapper.py')
