import sys
sys.path.insert(0, '.')

# Quick test of the Excel mapper
from src.utils.excel_mapper import ExcelColumnMapper
from src.models.database import db

# Check if database exists and has the new column
result = db.execute_query('PRAGMA table_info(products)')
cols = [c['name'] for c in result]

print('Database Columns:')
for c in cols:
    marker = ' <-- NEW' if c == 'available_stock' else ''
    print(f'  {c}{marker}')

if 'available_stock' in cols:
    print('\n✓ available_stock column exists (GENERATED column for stock - qty_sold)')
else:
    print('\n✗ available_stock column NOT found (will be added on init)')

# Check products table structure
result = db.execute_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
if result:
    print('\nProducts table definition:')
    print(result[0]['sql'][:500] + '...')

print('\n✓ Excel mapper module loaded successfully')
