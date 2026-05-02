# Update import section to derive cost_price from price_workshop
with open('robust_importer.py', 'r') as f:
    content = f.read()

# Find the import section where cost_price is set
old_cost = '''        # Prices - handle X/Y format
        price_cols = {}
        for price_type in ['cost_price', 'price_normal', 'price_workshop']:
            col = mapping.get(price_type)
            if col:
                price_cols[price_type] = col
        
        # Parse prices
        for price_type, col in price_cols.items():
            if col and pd.notna(row.get(col)):
                val = str(row[col]).strip()
                # Handle X/Y format: use first value for workshop, second for normal
                if '/' in val:
                    parts = val.split('/')
                    try:
                        prices = []
                        for part in parts:
                            cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                            if cleaned:
                                prices.append(float(cleaned))
                        
                        if price_type == 'price_workshop' and len(prices) > 0:
                            data['price_workshop'] = prices[0]
                        elif price_type == 'price_normal' and len(prices) > 1:
                            data['price_normal'] = prices[1]
                        elif price_type == 'cost_price' and len(prices) > 0:
                            data['cost_price'] = prices[0]
                    except ValueError:
                        pass
                else:
                    # Single value
                    try:
                        cleaned = ''.join(c for c in val if c.isdigit() or c == '.')
                        if cleaned:
                            data[price_type] = float(cleaned)
                    except ValueError:
                        pass
        
        # Set defaults if prices not parsed
        if 'price_workshop' not in data:
            data['price_workshop'] = data.get('price_normal', 0)
        if 'price_normal' not in data:
            data['price_normal'] = data.get('price_workshop', 0)
        if 'cost_price' not in data:
            data['cost_price'] = data.get('price_workshop', 0)'''

new_cost = '''        # Prices - handle X/Y format
        price_cols = {}
        for price_type in ['cost_price', 'price_normal', 'price_workshop']:
            col = mapping.get(price_type)
            if col:
                price_cols[price_type] = col
        
        # Parse prices
        for price_type, col in price_cols.items():
            if col and pd.notna(row.get(col)):
                val = str(row[col]).strip()
                # Handle X/Y format: use first value for workshop, second for normal
                if '/' in val:
                    parts = val.split('/')
                    try:
                        prices = []
                        for part in parts:
                            cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                            if cleaned:
                                prices.append(float(cleaned))
                        
                        if price_type == 'price_workshop' and len(prices) > 0:
                            data['price_workshop'] = prices[0]
                        elif price_type == 'price_normal' and len(prices) > 1:
                            data['price_normal'] = prices[1]
                        elif price_type == 'cost_price' and len(prices) > 0:
                            data['cost_price'] = prices[0]
                    except ValueError:
                        pass
                else:
                    # Single value
                    try:
                        cleaned = ''.join(c for c in val if c.isdigit() or c == '.')
                        if cleaned:
                            data[price_type] = float(cleaned)
                    except ValueError:
                        pass
        
        # Set defaults if prices not parsed
        # price_workshop is wholesale, price_normal is retail
        if 'price_workshop' not in data:
            data['price_workshop'] = data.get('price_normal', 0)
        if 'price_normal' not in data:
            data['price_normal'] = data.get('price_workshop', 0)
        # cost_price should be the wholesale price (what we pay)
        if 'cost_price' not in data:
            data['cost_price'] = data.get('price_workshop', 0)'''

if old_cost in content:
    content = content.replace(old_cost, new_cost)
    print('Updated cost_price handling')
else:
    print('Pattern not found, trying simpler version')
    # Just ensure cost_price defaults to price_workshop
    content = content.replace(
        "if 'cost_price' not in data:\n            data['cost_price'] = data.get('price_workshop', 0)",
        "if 'cost_price' not in data:\n            # Cost = wholesale price (price_workshop)\n            data['cost_price'] = data.get('price_workshop', 0)"
    )

with open('robust_importer.py', 'w') as f:
    f.write(content)

print('Updated price handling')
