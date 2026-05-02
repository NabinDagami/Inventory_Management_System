import re

# Test pattern matching
test_cases = [
    ('bikes names', 'name'),
    ('wholesale price/set', 'price_workshop'),
    ('retail price/set', 'price_normal'),
    ('qty in hand', 'stock'),
    ('qty sold', 'qty_sold'),
    ('available stock', 'stock'),
    ('status', 'description'),
]

patterns = {
    'name': [r'^(product\s*name|item|bike.*name|model)$', r'^(bikes?\s*name|item\s*name)$', r'company'],
    'price_workshop': [r'^wholesale\s*price$', r'^workshop\s*price$', r'^w/s\s*price$'],
    'price_normal': [r'^retail\s*price$', r'^price$', r'^normal\s*price$'],
    'stock': [r'^qty\s*in\s*hand$', r'^stock$', r'^quantity$'],
    'qty_sold': [r'^qty\s*sold$', r'^sold$'],
}

for col, expected in test_cases:
    matched = False
    for db_field, pat_list in patterns.items():
        for pattern in pat_list:
            if re.search(pattern, col, re.IGNORECASE):
                print(f"'{col}' -> {db_field} (expected {expected})")
                matched = True
                break
        if matched:
            break
    if not matched:
        print(f"'{col}' -> NO MATCH (expected {expected})")
