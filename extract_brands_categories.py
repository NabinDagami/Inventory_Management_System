import json
import pandas as pd
from collections import defaultdict

# Load the extracted data
with open('extracted_data/diwan_autoparts_data.json', 'r') as f:
    all_data = json.load(f)

# Analyze all categories for brand names
brands_found = defaultdict(set)
category_structure = {}

for category, items in all_data.items():
    category_structure[category] = {
        'total_items': len(items),
        'fields': list(items[0].keys()) if items else [],
        'brands': []
    }
    
    # Extract potential brand names from each category
    for item in items:
        for key, value in item.items():
            if isinstance(value, str):
                # Common brand indicators
                brand_keywords = ['Bajaj', 'Honda', 'Yamaha', 'Suzuki', 'TVS', 'Hero', 'Royal Enfield',
                                 'Aprilia', 'Benelli', 'KTM', 'BMW', 'Ducati', 'Harley', 'Triumph',
                                 'Pulsar', 'Unicorn', 'Shine', 'Splendor', 'Discover', 'FZ', 'RTR',
                                 'CBZ', 'Avenger', 'NTRQ', 'Jupiter', 'Gixxer', 'Enticer', 'Gladiator',
                                 'Duke', 'Apache', 'Ray', 'Dio', 'Activa', 'Winger', 'Grazia',
                                 'Access', 'Platina', 'Super Splendor', 'Passion', 'LML', 'Endurance',
                                 'Mesto', 'Varroc', 'Jainson', 'ABN', 'Superjit', 'Om', 'Nm',
                                 'F.C.C.', 'Ebdurance', 'B.S.F.C.', 'Endorance', 'Twin Disk',
                                 'M.R.F.', 'Ceat', 'Ajanta', 'TVS', 'KEF', 'Tornado']
                
                for brand in brand_keywords:
                    if brand.lower() in value.lower() and len(brand) > 2:
                        brands_found[category].add(brand)

# Print detailed analysis
print("=" * 80)
print("DIWAN AUTOPARTS - CATEGORY & BRAND ANALYSIS")
print("=" * 80)

print("\n[TOTAL CATEGORIES]:", len(all_data))
print("[TOTAL ITEMS]:", sum(len(items) for items in all_data.values()))

print("\n" + "=" * 80)
print("CATEGORY STRUCTURE & BRANDS")
print("=" * 80)

for category, info in category_structure.items():
    if info['total_items'] > 0:
        print(f"\n[Category] {category}")
        print(f"   Items: {info['total_items']}")
        print(f"   Fields: {', '.join(info['fields'])}")
        if brands_found[category]:
            print(f"   Brands: {', '.join(sorted(brands_found[category]))}")

# Show specific brand-rich categories
print("\n" + "=" * 80)
print("BRAND-SPECIFIC CATEGORIES")
print("=" * 80)

brand_categories = {
    'Brake Pad-Disk Pad': 'Brake Components',
    'Chainkit': 'Chain Kits',
    'Clutch Plate': 'Clutch Components',
    'Air Filter': 'Filters',
    'Mirror': 'Mirrors',
    'Tyres': 'Tyres',
    'Mobil': 'Oils & Lubricants',
    'Shock Rod': 'Suspension',
    'Petrol Tap': 'Fuel System',
    'Self-Carbon': 'Carbon Parts',
}

for cat_key, cat_name in brand_categories.items():
    if cat_key in all_data:
        items = all_data[cat_key]
        print(f"\n[Component] {cat_name} ({cat_key}) - {len(items)} items")
        shown = 0
        for item in items:
            for key, val in item.items():
                if val and str(val).strip() and 'names' not in str(val).lower() and 'Company' not in str(val) and 'Bike' not in str(val):
                    print(f"   * {val}")
                    shown += 1
                    break
            if shown >= 5:
                break

# Extract unique brands across all categories
all_brands = set()
for category_brands in brands_found.values():
    all_brands.update(category_brands)

print("\n" + "=" * 80)
print("ALL UNIQUE BRANDS FOUND")
print("=" * 80)
print(f"\nTotal unique brands: {len(all_brands)}")
print("\nBrands: " + ", ".join(sorted(all_brands)))

# Save categorized data
categorized = {
    'metadata': {
        'total_categories': len(all_data),
        'total_items': sum(len(items) for items in all_data.values()),
        'total_brands': len(all_brands)
    },
    'categories': category_structure,
    'brands_by_category': {k: list(v) for k, v in brands_found.items()},
    'all_brands': sorted(list(all_brands))
}

with open('extracted_data/categorized_data.json', 'w') as f:
    json.dump(categorized, f, indent=2, ensure_ascii=False)

print("\n[SUCCESS] Categorized data saved to: extracted_data/categorized_data.json")
