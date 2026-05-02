import re

def clean_column_name(col_name):
    if pd.isna(col_name):
        return ''
    name = str(col_name).strip()
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    return name.lower().strip()

import pandas as pd

# Test with actual data
xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
df = pd.read_excel(xl, sheet_name='Brake Pad-Disk Pad', header=None)

# Read with header=1 (row 1 is the header row)
df_data = pd.read_excel(xl, sheet_name='Brake Pad-Disk Pad', header=1)

print('Original columns:', df_data.columns.tolist())

cleaned = [clean_column_name(col) for col in df_data.columns]
print('Cleaned columns:', cleaned)

# Test pattern matching
patterns = {
    'name': [r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'],
    'price_workshop': [r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*'],
    'price_normal': [r'^retail.*', r'^price.*', r'^normal.*'],
    'stock': [r'^qty.*hand$', r'^stock$', r'^quantity$', r'^available.*stock$'],
    'qty_sold': [r'^qty.*sold$', r'^sold$'],
    'status': [r'^status$'],
}

for col in cleaned:
    matched = False
    for db_field, pat_list in patterns.items():
        for pattern in pat_list:
            if re.search(pattern, col, re.IGNORECASE):
                print(f"  '{col}' -> {db_field}")
                matched = True
                break
        if matched:
            break