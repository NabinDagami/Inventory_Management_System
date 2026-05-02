"""
Preview & Import Script for Diwan Autoparts
Shows what will be imported before adding to database
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import db

EXCLUDE_SHEETS = ['Home', 'Home ', 'Dashboard', 'Sheet1', 'Daya form', '/']

def clean_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip()
        if val == '':
            return None
    return val

def parse_price(price_val):
    if pd.isna(price_val):
        return None, None
    price_str = str(price_val).strip()
    if '/' in price_str:
        parts = price_str.split('/')
        numeric_parts = []
        for part in parts:
            try:
                cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                if cleaned:
                    numeric_parts.append(float(cleaned))
            except:
                pass
        if len(numeric_parts) >= 2:
            return numeric_parts[0], numeric_parts[1]
        elif len(numeric_parts) == 1:
            return numeric_parts[0], numeric_parts[0]
    try:
        cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
        if cleaned:
            price = float(cleaned)
            return price, price
    except:
        pass
    return None, None

def find_header_row(df):
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
        if any(k in row_str for k in ['company', 'items', 'bike', 'price', 'qty', 'stock', 'bikes names']):
            return idx
    return None

def preview_excel_data(excel_path):
    """Extract and preview all data from Excel without importing"""
    
    print("=" * 80)
    print("PREVIEW MODE - Analyzing Excel File")
    print("=" * 80)
    
    if not os.path.exists(excel_path):
        print(f"\n❌ Error: File '{excel_path}' not found!")
        return None
    
    excel_file = pd.ExcelFile(excel_path)
    
    preview_data = {
        'sheets': [],
        'categories': set(),
        'brands': set(),
        'products': []
    }
    
    for sheet_name in excel_file.sheet_names:
        if sheet_name in EXCLUDE_SHEETS or sheet_name.startswith('/'):
            continue
        
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        if len(df) < 2:
            continue
        
        header_row_idx = find_header_row(df)
        if header_row_idx is None:
            continue
        
        df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row_idx)
        
        # Map columns
        column_mapping = {}
        for col in df_data.columns:
            col_str = str(col).lower().strip()
            if any(k in col_str for k in ['company names', 'items', 'bike names', 'bikes names', 'bearing size', 'tyre sizes']):
                column_mapping[col] = 'product_name'
            elif any(k in col_str for k in ['company', 'brand']) and 'company names' not in col_str:
                column_mapping[col] = 'company'
            elif any(k in col_str for k in ['wholesale', 'w/s']):
                column_mapping[col] = 'wholesale_price'
            elif any(k in col_str for k in ['retail']):
                column_mapping[col] = 'retail_price'
            elif 'price' in col_str:
                column_mapping[col] = 'price'
            elif any(k in col_str for k in ['qty in hand', 'quantity in hand', 'stock']):
                column_mapping[col] = 'qty_in_hand'
            elif 'status' in col_str:
                column_mapping[col] = 'status'
        
        seen_targets = set()
        filtered_mapping = {}
        for source, target in column_mapping.items():
            if target not in seen_targets:
                filtered_mapping[source] = target
                seen_targets.add(target)
        df_data.rename(columns=filtered_mapping, inplace=True)
        
        # Extract products from this sheet
        sheet_products = []
        current_company = None
        
        for idx, row in df_data.iterrows():
            try:
                if row.isna().all():
                    continue
            except:
                all_empty = True
                for val in row.values:
                    if pd.notna(val):
                        all_empty = False
                        break
                if all_empty:
                    continue
            
            company_val = str(row.get('company', '')).strip()
            if company_val.upper() == sheet_name.upper():
                continue
            
            product = {'category': sheet_name}
            
            if 'company' in df_data.columns:
                company = clean_value(row.get('company'))
                if company:
                    current_company = company
                product['brand'] = current_company or 'Generic'
            else:
                product['brand'] = 'Generic'
            
            if 'product_name' in df_data.columns:
                product['product_name'] = clean_value(row.get('product_name'))
            
            if not product.get('product_name'):
                continue
            
            # Prices
            wholesale_price = None
            retail_price = None
            
            if 'wholesale_price' in df_data.columns:
                wp = clean_value(row.get('wholesale_price'))
                if wp:
                    wholesale, retail = parse_price(wp)
                    wholesale_price = wholesale
                    retail_price = retail
            
            if 'retail_price' in df_data.columns:
                rp = clean_value(row.get('retail_price'))
                if rp:
                    _, retail = parse_price(rp)
                    retail_price = retail
            
            if 'price' in df_data.columns:
                price = clean_value(row.get('price'))
                if price:
                    wholesale, retail = parse_price(price)
                    if wholesale_price is None:
                        wholesale_price = wholesale
                    if retail_price is None:
                        retail_price = retail
            
            product['cost_price'] = wholesale_price or 0
            product['normal_price'] = retail_price or wholesale_price or 0
            
            # Stock
            if 'qty_in_hand' in df_data.columns:
                try:
                    qty = clean_value(row.get('qty_in_hand'))
                    product['stock'] = int(float(qty)) if qty else 0
                except:
                    product['stock'] = 0
            else:
                product['stock'] = 0
            
            preview_data['categories'].add(sheet_name)
            preview_data['brands'].add(product['brand'])
            preview_data['products'].append(product)
            sheet_products.append(product)
        
        if sheet_products:
            preview_data['sheets'].append({
                'name': sheet_name,
                'count': len(sheet_products)
            })
    
    return preview_data

def show_preview(preview_data):
    """Display preview of what will be imported"""
    
    print("\n" + "=" * 80)
    print("IMPORT PREVIEW")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Sheets to process: {len(preview_data['sheets'])}")
    print(f"   • New categories: {len(preview_data['categories'])}")
    print(f"   • New brands: {len(preview_data['brands'])}")
    print(f"   • Total products: {len(preview_data['products'])}")
    
    print(f"\n📁 SHEETS ({len(preview_data['sheets'])}):")
    for sheet in preview_data['sheets'][:10]:
        print(f"   • {sheet['name']}: {sheet['count']} products")
    if len(preview_data['sheets']) > 10:
        print(f"   ... and {len(preview_data['sheets']) - 10} more sheets")
    
    print(f"\n🏷️  CATEGORIES ({len(preview_data['categories'])}):")
    for cat in sorted(list(preview_data['categories']))[:15]:
        print(f"   • {cat}")
    if len(preview_data['categories']) > 15:
        print(f"   ... and {len(preview_data['categories']) - 15} more")
    
    print(f"\n🏭 BRANDS ({len(preview_data['brands'])}):")
    for brand in sorted(list(preview_data['brands']))[:15]:
        print(f"   • {brand}")
    if len(preview_data['brands']) > 15:
        print(f"   ... and {len(preview_data['brands']) - 15} more")
    
    print("\n📦 SAMPLE PRODUCTS (first 10):")
    print("-" * 80)
    for i, p in enumerate(preview_data['products'][:10], 1):
        print(f"{i}. {p['product_name'][:45]}")
        print(f"   Category: {p['category']} | Brand: {p['brand']}")
        print(f"   Stock: {p['stock']} | Cost: ₹{p['cost_price']} | Price: ₹{p['normal_price']}")
    
    print("\n" + "=" * 80)

def import_to_database(preview_data):
    """Actually import the data to database"""
    from utils.sku_generator import SKUGenerator
    
    print("\n" + "=" * 80)
    print("IMPORTING TO DATABASE...")
    print("=" * 80)
    
    total_imported = 0
    
    # Create categories first
    category_ids = {}
    for cat_name in preview_data['categories']:
        result = db.execute_query(
            "SELECT category_id FROM categories WHERE category_name = ?",
            (cat_name,)
        )
        if result:
            category_ids[cat_name] = result[0]['category_id']
            print(f"   ✓ Category exists: {cat_name}")
        else:
            cat_id = db.execute_insert(
                "INSERT INTO categories (category_name, description) VALUES (?, ?)",
                (cat_name, f"Imported from Excel")
            )
            category_ids[cat_name] = cat_id
            print(f"   + Created category: {cat_name}")
    
    # Create brands
    brand_ids = {}
    for brand_name in preview_data['brands']:
        brand_name = str(brand_name).strip().upper()
        result = db.execute_query(
            "SELECT brand_id FROM brands WHERE brand_name = ?",
            (brand_name,)
        )
        if result:
            brand_ids[brand_name] = result[0]['brand_id']
        else:
            brand_id = db.execute_insert(
                "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
                (brand_name, "Imported from Excel")
            )
            brand_ids[brand_name] = brand_id
            print(f"   + Created brand: {brand_name}")
    
    # Import products
    print("\n   Importing products...")
    for product in preview_data['products']:
        cat_id = category_ids.get(product['category'])
        brand_id = brand_ids.get(str(product['brand']).upper())
        
        if not cat_id or not brand_id:
            continue
        
        try:
            sku = SKUGenerator.generate_sku(cat_id, brand_id)
            
            db.execute_insert("""
                INSERT INTO products (
                    name, sku, category_id, brand_id,
                    stock, price_normal, price_workshop, cost_price,
                    reorder_level, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product['product_name'],
                sku,
                cat_id,
                brand_id,
                product['stock'],
                product['normal_price'],
                product['normal_price'],
                product['cost_price'],
                10,
                1
            ))
            total_imported += 1
        except Exception as e:
            print(f"   ✗ Error: {product['product_name'][:30]}... - {e}")
    
    print(f"\n   ✅ Imported {total_imported} products successfully!")
    return total_imported

def main():
    excel_path = 'Diwan Autoparts backup.xlsx'
    
    print("=" * 80)
    print("EXCEL IMPORT TOOL - Preview Mode")
    print("=" * 80)
    
    # Preview mode
    preview_data = preview_excel_data(excel_path)
    
    if not preview_data or not preview_data['products']:
        print("\n❌ No data found to import!")
        return
    
    show_preview(preview_data)
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will add data to your database.")
    print("   Existing data will NOT be deleted or modified.")
    print("\n   Options:")
    print("   [1] Import all data to database")
    print("   [2] Cancel - Don't import anything")
    
    try:
        choice = input("\n   Enter your choice (1 or 2): ").strip()
    except KeyboardInterrupt:
        print("\n\n   Cancelled by user.")
        return
    
    if choice == '1':
        import_to_database(preview_data)
        
        # Show final stats
        total = db.execute_query('SELECT COUNT(*) as count FROM products')[0]['count']
        print(f"\n   📊 Total products in database now: {total}")
        print("\n   🎉 Import complete! You can now open your Inventory Management app.")
    else:
        print("\n   ❌ Import cancelled. No changes were made to the database.")

if __name__ == "__main__":
    main()
