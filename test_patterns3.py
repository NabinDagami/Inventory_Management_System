import re

patterns = {
    'name': [r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', r'^.*item.*$', r'^.*product.*$'],
    'price_workshop': [r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*'],
    'price_normal': [r'^retail.*', r'^price.*', r'^normal.*'],
    'stock': [r'^qty.*hand$', r'^stock$', r'^quantity$', r'^available.*stock$'],
    'qty_sold': [r'^qty.*sold$', r'^sold$'],
    'status': [r'^status$'],
    'cost_price': [r'^cost.*price$', r'^purchase.*price$'],
    'reorder_level': [r'^reorder.*level$', r'^min.*stock$'],
    'description': [r'^description$'],
}

test_cases = [
    ('bikes names', 'name'),
    ('wholesale price/set', 'price_workshop'),
    ('retail price/set', 'price_normal'),
    ('qty in hand', 'stock'),
    ('qty sold', 'qty_sold'),
    ('available stock', 'stock'),
    ('status', 'status'),
]

for col, expected in test_cases:
    matched = False
    for db_field, pat_list in patterns.items():
        for pattern in pat_list:
            if re.search(pattern, col, re.IGNORECASE):
                status = 'OK' if db_field == expected else 'WRONG'
                print(f"{status}: '{col}' -> {db_field} (expected {expected})")
                matched = True
                break
        if matched:
            break
    if not matched:
        print(f"FAIL: '{col}' -> NO MATCH (expected {expected})")
