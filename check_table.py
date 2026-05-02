from src.models.database import db

# Check the CREATE TABLE statement
result = db.execute_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
if result:
    print('CREATE TABLE statement:')
    print(result[0]['sql'])
    print()
    # Check for available_stock in the definition
    if 'available_stock' in result[0]['sql'].lower():
        print('available_stock IS in the table definition')
    else:
        print('available_stock IS NOT in the table definition')
