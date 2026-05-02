import pandas as pd

# Read Excel
xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
sheet_name = 'Brake Pad-Disk Pad'

# Read with header
df_data = pd.read_excel(xl, sheet_name=sheet_name, header=1)

# Clean column names
import re
def clean_column_name(col_name):
    if pd.isna(col_name):
        return ''
    name = str(col_name).strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.lower().strip()

df_data.columns = [clean_column_name(col) for col in df_data.columns]
print('Cleaned columns:', df_data.columns.tolist())

# Pattern matching
patterns = {
    'name': [r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'],
    'sku': [r'^sku$', r'^code$', r'product.*code'],
    'category': [r'^category$', r'^type$'],
    'brand': [r'^brand$', r'^company$', r'^manufacturer$'],
    'stock': [r'^qty.*hand$', r'^stock$', r'^quantity$'],
    'qty_sold': [r'^qty.*sold$', r'^sold$'],
    'price_normal': [r'^retail.*', r'^price.*', r'^normal.*'],
    'price_workshop': [r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*'],
    'cost_price': [r'^cost.*price$', r'^purchase.*price$'],
    'reorder_level': [r'^reorder.*level$', r'^min.*stock$'],
}

mapping = {}
for db_field, pat_list in patterns.items():
    for excel_col in df_data.columns:
        for pattern in pat_list:
            if re.search(pattern, excel_col, re.IGNORECASE):
                if db_field not in mapping:
                    mapping[db_field] = excel_col
                    print(f"  Mapped: '{excel_col}' -> {db_field}")
                    break

print(f'\nTotal mappings: {len(mapping)}')
print(f'Mapping: {mapping}')
