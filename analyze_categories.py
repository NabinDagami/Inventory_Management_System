import json
import pandas as pd

# Load the extracted data
with open('extracted_data/diwan_autoparts_data.json', 'r') as f:
    all_data = json.load(f)

# Check the Others category which seems to have mixed items
others = all_data.get('Others', [])
print("=== OTHERS CATEGORY (First 20 items) ===")
for i, item in enumerate(others[:20]):
    print(f"{i+1}. {item}")

# Check original Excel to see category structure
xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
print(f"\n=== ORIGINAL SHEETS (Categories) ===")
for i, sheet in enumerate(xl.sheet_names):
    print(f"{i+1}. {sheet}")

# Show sample data from various categories to find brand names
print(f"\n=== SAMPLE DATA FROM KEY CATEGORIES ===")
categories_to_check = ['Brake Pad-Disk Pad', 'Chainkit', 'Clutch Plate', 'Air Filter', 'Others']
for cat in categories_to_check:
    if cat in all_data:
        print(f"\n{cat}:")
        for item in all_data[cat][:3]:  # First 3 items
            print(f"  {item}")
