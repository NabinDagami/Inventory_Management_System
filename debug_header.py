import pandas as pd
from src.models.database import db

xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
sheet_name = 'Brake Pad-Disk Pad'

# Read without headers first
df_raw = pd.read_excel(xl, sheet_name=sheet_name, header=None)
print(f'Sheet: {sheet_name}')
print(f'Raw rows: {len(df_raw)}, raw cols: {len(df_raw.columns)}')
print('First few rows:')
print(df_raw.head(3).to_string())
print()

# Find header row
max_check = min(10, len(df_raw))
for idx in range(max_check):
    row = df_raw.iloc[idx]
    row_str = ' '.join([str(x).lower().strip() for x in row if pd.notna(x)])
    header_indicators = ['name', 'price', 'cost', 'sku', 'category', 'brand', 'stock', 'qty', 'product']
    matches = sum(1 for indicator in header_indicators if indicator in row_str)
    print(f'Row {idx}: matches={matches}, content={row_str[:80]}')
    if matches >= 2:
        print(f'  -> Found header row at index {idx}')
        header_row_idx = idx
        break
else:
    header_row_idx = None

print(f'\nHeader row index: {header_row_idx}')

if header_row_idx is not None:
    df_data = pd.read_excel(xl, sheet_name=sheet_name, header=header_row_idx)
    print(f'\nData rows: {len(df_data)}')
    print(f'Columns: {df_data.columns.tolist()}')
    print('\nFirst 3 rows:')
    print(df_data.head(3).to_string())
