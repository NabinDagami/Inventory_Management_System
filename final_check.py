print('=' * 80)
print('FINAL VALIDATION - DIWAN AUTOPARTS IMPLEMENTATION')
print('=' * 80)

# 1. Check all modified files exist
import os
files = [
    'src/models/database.py',
    'import_excel_to_db.py',
    'src/utils/excel_importer.py',
    'src/utils/excel_mapper.py',
]

print('\n1. FILE VERIFICATION')
for f in files:
    exists = os.path.exists(f)
    status = 'OK' if exists else 'MISSING'
    print(f'   [{status}] {f}')

# 2. Check database schema
print('\n2. DATABASE SCHEMA')
from src.models.database import db
result = db.execute_query('PRAGMA table_info(products)')
cols = {c['name'] for c in result}

required_cols = {'stock', 'qty_sold', 'price_normal', 'price_workshop', 'cost_price', 'available_stock'}
for col in required_cols:
    status = 'OK' if col in cols else 'MISSING'
    print(f'   [{status}] {col}')

# 3. Check generated column
print('\n3. GENERATED COLUMN TEST')
db.execute_insert("INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold, price_normal, price_workshop, cost_price, reorder_level, is_active) VALUES ('Test Gen', 'TEST-GEN', 1, 1, 50, 10, 200.0, 150.0, 100.0, 5, 1)")
result = db.execute_query("SELECT stock, qty_sold, available_stock FROM products WHERE sku='TEST-GEN'")
if result:
    p = result[0]
    expected = p['stock'] - p['qty_sold']
    actual = p['available_stock']
    status = 'OK' if actual == expected else 'FAIL'
    print(f'   [{status}] available_stock = {actual} (expected {expected})')
db.execute_update("DELETE FROM products WHERE sku='TEST-GEN'")

# 4. Check price parsing
print('\n4. PRICE PARSING')
try:
    from excel_data_mapper import parse_price
    ws, normal = parse_price('180/250')
    status = 'OK' if (ws == 180 and normal == 250) else 'FAIL'
    print(f'   [{status}] X/Y format: 180/250 -> workshop={ws}, normal={normal}')
    
    ws, normal = parse_price('180')
    status = 'OK' if (ws == 180 and normal == 180) else 'FAIL'
    print(f'   [{status}] Single value: 180 -> workshop={ws}, normal={normal}')
except ImportError:
    print('   [SKIP] excel_data_mapper not available')
except Exception as e:
    print(f'   [FAIL] Error: {e}')

# 5. Check key functions
print('\n5. KEY FUNCTIONS')
try:
    from import_excel_to_db import parse_price as parse_price2
    print('   [OK] import_excel_to_db.parse_price available')
except ImportError as e:
    print(f'   [FAIL] {e}')

# 6. Verify no syntax errors
print('\n6. SYNTAX CHECK')
import py_compile
try:
    py_compile.compile('src/utils/excel_mapper.py', doraise=True)
    print('   [OK] src/utils/excel_mapper.py')
except py_compile.PyCompileError:
    print('   [FAIL] src/utils/excel_mapper.py has syntax errors')

try:
    py_compile.compile('import_excel_to_db.py', doraise=True)
    print('   [OK] import_excel_to_db.py')
except py_compile.PyCompileError:
    print('   [FAIL] import_excel_to_db.py has syntax errors')

print('\n' + '=' * 80)
print('VALIDATION COMPLETE')
print('=' * 80)
