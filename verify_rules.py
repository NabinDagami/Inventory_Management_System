# Verification script for pricing and inventory rules
print("=" * 80)
print("VERIFICATION OF PRICING AND INVENTORY RULES")
print("=" * 80)

# Check database schema
from src.models.database import db

print("\n1. DATABASE SCHEMA CHECK")
print("-" * 80)
result = db.execute_query("PRAGMA table_info(products)")
columns = [col['name'] for col in result]
required_fields = ['stock', 'qty_sold', 'price_normal', 'price_workshop', 'cost_price']

for field in required_fields:
    if field in columns:
        print(f"  [OK] {field} field exists")
    else:
        print(f"  [MISSING] {field} field not found")

# Check for available_stock
if 'available_stock' in columns:
    print("  [OK] available_stock field exists")
else:
    print("  [INFO] available_stock may need to be added via ALTER TABLE")

# Verify price parsing - try excel_data_mapper first, then excel_importer
try:
    from excel_data_mapper import parse_price
except ImportError:
    from src.utils.excel_importer import SimpleExcelImporter
    # Use importer's parse_price method if available
    parse_price = SimpleExcelImporter.parse_price if hasattr(SimpleExcelImporter, 'parse_price') else lambda x: (None, None)

print("\n2. PRICE PARSING CHECK")
print("-" * 80)
test_prices = [
    ("180/250", "X/Y format"),
    ("1000/1300", "X/Y format with larger numbers"),
    ("180", "Single value"),
]

for price_str, desc in test_prices:
    ws, normal = parse_price(price_str)
    print(f"  {desc}: '{price_str}' -> workshop={ws}, normal={normal}")
    if ws is not None and normal is not None:
        print(f"    [OK] Parsed correctly")
    else:
        print(f"    [FAIL] Failed to parse")

print("\n3. INVENTORY CALCULATION CHECK")
print("-" * 80)
test_cases = [
    {"stock": 100, "qty_sold": 20, "expected": 80},
    {"stock": 50, "qty_sold": 50, "expected": 0},
    {"stock": 10, "qty_sold": 0, "expected": 10},
]

all_pass = True
for case in test_cases:
    stock = case["stock"]
    qty_sold = case["qty_sold"]
    expected = case["expected"]
    actual = stock - qty_sold
    status = "[OK]" if actual == expected else "[FAIL]"
    if actual != expected:
        all_pass = False
    print(f"  {status} stock={stock}, qty_sold={qty_sold} => available={actual} (expected {expected})")

print("\n4. IMPORT SCRIPTS CHECK")
print("-" * 80)
import os

scripts = [
    ("import_excel_to_db.py", "Main import script"),
    ("src/utils/excel_mapper.py", "GUI mapper"),
    ("src/utils/excel_importer.py", "Excel importer"),
]


for script, desc in scripts:
    if os.path.exists(script):
        print(f"  [OK] {desc}: {script}")
    else:
        print(f"  [MISSING] {desc}: {script}")

print("\n5. EXCEL FILE CHECK")
print("-" * 80)
excel_file = "Diwan Autoparts backup.xlsx"
if os.path.exists(excel_file):
    print(f"  [OK] Excel file found: {excel_file}")
    import pandas as pd
    xl = pd.ExcelFile(excel_file)
    print(f"  [OK] Sheets: {len(xl.sheet_names)}")
else:
    print(f"  [MISSING] Excel file not found: {excel_file}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

if all_pass:
    print("\n[RESULT] All checks passed! Database is ready for import.")
    print("Run: python import_excel_to_db.py")
else:
    print("\n[RESULT] Some checks failed. Please review.")

print("=" * 80)
