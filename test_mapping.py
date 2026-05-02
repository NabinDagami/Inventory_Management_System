import re
import pandas as pd

def clean_column_name(col_name):
    import pandas as pd
    if pd.isna(col_name):
        return ''
    name = str(col_name).strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.lower().strip()

def map_columns(excel_columns, patterns):
    mapping = {}
    for db_field, pat_list in patterns.items():
        for excel_col in excel_columns:
            for pattern in pat_list:
                if re.search(pattern, excel_col, re.IGNORECASE):
                    if db_field not in mapping:
                        mapping[db_field] = excel_col
                        print(f"  Mapped: '{excel_col}' -> {db_field}")
                        break
    return mapping

xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
df_data = pd.read_excel(xl, sheet_name='Brake Pad-Disk Pad', header=1)

cleaned = [clean_column_name(col) for col in df_data.columns]
print('Cleaned columns:', cleaned)
print()

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

print('Column mapping:')
mapping = map_columns(cleaned, patterns)
print(f'\nResult: {mapping}')
