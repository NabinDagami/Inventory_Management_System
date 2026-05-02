import json

# Load the data
with open('extracted_data/diwan_autoparts_data.json', 'r') as f:
    all_data = json.load(f)

with open('extracted_data/categories_and_brands.json', 'r') as f:
    combined = json.load(f)

# Display detailed category-brand mapping
print("=" * 100)
print("DETAILED CATEGORY-BRAND MAPPING WITH SAMPLE ITEMS")
print("=" * 100)

for category in sorted(all_data.keys()):
    items = all_data[category]
    info = combined['category_summary'][category]
    brands = info['brands']
    
    print(f"\n{'-' * 100}")
    print(f"[CATEGORY] {category}")
    print(f"   Items: {info['item_count']} | Brands: {', '.join(brands) if brands else 'General/Misc'}")
    print(f"{'-' * 100}")
    
    # Show sample items
    shown = 0
    for item in items[:5]:  # Show first 5 items
        for key, value in item.items():
            if value and str(value).strip() and str(value) != 'nan':
                print(f"   * {value}")
                shown += 1
                break
        if shown >= min(5, len(items)):
            break
    
    if len(items) > 5:
        print(f"   ... and {len(items) - 5} more items")

print(f"\n{'=' * 100}")
print("COMPLETE BRAND DISTRIBUTION")
print(f"{'=' * 100}")

# Reverse mapping: brands -> categories
brand_categories = {}
for cat, brands_list in combined['category_summary'].items():
    for brand in brands_list['brands']:
        if brand not in brand_categories:
            brand_categories[brand] = []
        brand_categories[brand].append(cat)

print("\nBrands appearing in most categories:")
for brand, cats in sorted(brand_categories.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    print(f"  * {brand:<20} -> {len(cats)} categories: {', '.join(cats[:5])}{'...' if len(cats) > 5 else ''}")

print(f"\n{'=' * 100}")
