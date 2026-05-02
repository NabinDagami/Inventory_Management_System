import json
import pandas as pd
from collections import defaultdict

# Load the extracted data
with open('extracted_data/diwan_autoparts_data.json', 'r') as f:
    all_data = json.load(f)

# Analyze all categories for brand names
brands_by_category = defaultdict(set)
category_items = {}

for category, items in all_data.items():
    category_items[category] = len(items)
    
    # Extract potential brand names from each category
    for item in items:
        for key, value in item.items():
            if isinstance(value, str) and value.strip():
                # Common brand/model indicators
                brand_keywords = [
                    'Bajaj', 'Honda', 'Yamaha', 'Suzuki', 'TVS', 'Hero', 'Royal Enfield',
                    'Aprilia', 'Benelli', 'KTM', 'BMW', 'Duke', 'Apache',
                    'Pulsar', 'Unicorn', 'Shine', 'Splendor', 'Discover', 'FZ', 'RTR', 'Fazer',
                    'CBZ', 'Avenger', 'NTRQ', 'Jupiter', 'Gixxer', 'Enticer', 'Gladiator',
                    'Ray', 'Dio', 'Activa', 'Winger', 'Grazia', 'Access', 'Platina',
                    'Super Splendor', 'Passion', 'LML', 'Endurance', 'Mesto', 'Varroc',
                    'Jainson', 'ABN', 'Superjit', 'Om', 'Nm', 'F.C.C.', 'Ebdurance',
                    'B.S.F.C.', 'Endorance', 'Twin Disk', 'M.R.F.', 'Ceat', 'Ajanta',
                    'KEF', 'Tornado', 'Bullet', 'X', 'Crux', 'V3', 'V2', 'Carbon', 'Kit'
                ]
                
                for brand in brand_keywords:
                    if brand.lower() in value.lower():
                        brands_by_category[category].add(brand)

# Create combined view
print("=" * 100)
print("DIWAN AUTOPARTS INVENTORY - CATEGORIES AND BRANDS OVERVIEW")
print("=" * 100)

# Table header
print(f"\n{'Category':<45} {'Items':>6} {'Brands/Models'}")
print("-" * 100)

total_items = 0
for category in sorted(all_data.keys()):
    item_count = category_items.get(category, 0)
    total_items += item_count
    
    brands = sorted(list(brands_by_category.get(category, set())))
    
    if brands:
        # Format brands nicely
        brand_str = ", ".join(brands[:8])  # Show first 8
        if len(brands) > 8:
            brand_str += f" +{len(brands)-8} more"
        print(f"{category:<45} {item_count:>6}   {brand_str}")
    else:
        print(f"{category:<45} {item_count:>6}   (General/Misc)")

print("-" * 100)
print(f"{'TOTAL':<45} {total_items:>6}")

# Summary statistics
print("\n" + "=" * 100)
print("SUMMARY STATISTICS")
print("=" * 100)

# All unique brands
all_brands = set()
for brands in brands_by_category.values():
    all_brands.update(brands)

print(f"\nTotal Categories: {len(all_data)}")
print(f"Total Items: {total_items}")
print(f"Total Unique Brands/Models: {len(all_brands)}")

# Categories with most brands
print("\n[Categories with Most Brands]")
cat_brand_counts = [(cat, len(brands)) for cat, brands in brands_by_category.items()]
cat_brand_counts.sort(key=lambda x: x[1], reverse=True)
for cat, count in cat_brand_counts[:10]:
    brands_list = sorted(list(brands_by_category[cat]))
    print(f"  {cat:<40} ({count} brands): {', '.join(brands_list[:5])}{'...' if len(brands_list) > 5 else ''}")

# Categorize by type
print("\n" + "=" * 100)
print("CATEGORIES BY TYPE")
print("=" * 100)

category_groups = {
    'Engine Components': ['Cylinder', 'Piston Ring', 'Crankshaft', 'Rocker Arm', 'Camshaft', 'Timing Chain', 'Clutch Plate', 'Oil Pump'],
    'Transmission': ['Gear Lever', 'Gear Shaft', 'Shift Fork', 'Selector Fork', 'Main Shaft'],
    'Brakes': ['Brake Shoe', 'Brake Pad', 'Brake Lining', 'Cylinder Assembly', 'Disc Plate', 'Disc Caliber'],
    'Electrical': ['Dipper Switch', 'Head Light', 'Speedo Meter', 'Self-Cutout', 'Self-Relay', 'Indicator', 'Battery'],
    'Suspension': ['Shock Rod', 'Shock Spring', 'Suspension Bush', 'Side Stand'],
    'Fuel System': ['Petrol Tap', 'Float Valve', 'Strainer', 'Carburator'],
    'Body Parts': ['Seat Cover', 'Side Light', 'Self-Carbon', 'Top', 'Rektifire', 'Mirror', 'Tank Cap'],
    'Bearings': ['Bearing', 'One Way Bearing'],
    'Filters': ['Air Filter', 'Oil Filter'],
    'Fluids': ['Mobil', 'Oil'],
    'Fasteners': ['Male-Female', 'Clutch Cable', 'Choke Cable'],
    'Tires & Tubes': ['Tyres', 'Tube'],
    'Other': []
}

print("\n[Grouped Categories]")
for group_name, keywords in category_groups.items():
    matching = []
    for cat in all_data.keys():
        if any(kw.lower() in cat.lower() for kw in keywords):
            matching.append(cat)
    if matching:
        print(f"\n  {group_name}:")
        for cat in matching:
            brands = sorted(list(brands_by_category.get(cat, set())))
            print(f"    • {cat} ({len(all_data[cat])} items) - {', '.join(brands[:3])}{'...' if len(brands) > 3 else ''}")

# Save combined data
combined = {
    'category_summary': {},
    'all_brands': sorted(list(all_brands)),
    'total_categories': len(all_data),
    'total_items': total_items
}

for category in all_data.keys():
    combined['category_summary'][category] = {
        'item_count': category_items.get(category, 0),
        'brands': sorted(list(brands_by_category.get(category, set())))
    }

with open('extracted_data/categories_and_brands.json', 'w') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Combined categories & brands saved to: extracted_data/categories_and_brands.json")
print("=" * 100)
