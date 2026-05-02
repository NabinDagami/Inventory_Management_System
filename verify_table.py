from src.models.database import db

# Get detailed table info
result = db.execute_query("SELECT * FROM sqlite_master WHERE type='table' AND name='products'")
if result:
    print('Products table definition:')
    print(result[0]['sql'])
    print()
    if 'available_stock' in result[0]['sql'].lower():
        print('OK: available_stock IS in the table definition (as GENERATED column)')
    else:
        print('FAIL: available_stock NOT in table definition')
