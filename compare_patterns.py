import re

# Current patterns
old_patterns = {
    'name': [
        r'^(product\s*name|item|bike.*name|model)$',
        r'^(bikes?\s*name|item\s*name)$',
        r'company',
    ],
    'price_workshop': [
        r'^wholesale\s*price$',
        r'^workshop\s*price$',
        r'^w/s\s*price$',
    ],
}

# New patterns
new_patterns = {
    'name': [
        r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', 
        r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'
    ],
    'price_workshop': [
        r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*',
    ],
}

test_cases = [
    ('bikes names', 'name'),
    ('wholesale price/set', 'price_workshop'),
]

for col, expected_field in test_cases:
    for field, patterns in [('old', old_patterns), ('new', new_patterns)]:
        matched = False
        if field == 'old':
            for pat_list in patterns.values():
                for pattern in pat_list:
                    if re.search(pattern, col, re.IGNORECASE):
                        matched = True
                        break
                if matched:
                    break
        else:
            if expected_field in patterns:
                for pattern in patterns[expected_field]:
                    if re.search(pattern, col, re.IGNORECASE):
                        matched = True
                        break
        
        status = 'OK' if matched else 'FAIL'
        print(f"{field:4s}: {col:25s} -> {status}")
