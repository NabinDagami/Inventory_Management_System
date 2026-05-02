"""
Direct Excel to Database Import Script for Diwan Autoparts
Reads 'Diwan Autoparts backup.xlsx' and imports directly into inventory.db
"""

import pandas as pd
import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import db
from utils.sku_generator import SKUGenerator

# Sheets to exclude (non-data sheets)
EXCLUDE_SHEETS = ['Home', 'Home ', 'Dashboard', 'Sheet1', 'Daya form', '/']

def clean_value(val):
    """Clean and convert values"""
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip()
        if val == '':
            return None
    return val

def parse_price(price_val):
    """
    Extract numeric prices from various formats:
    - '180/250' -> wholesale=180, retail=250 (workshop_price=180, price_normal=250)
    - '180' -> wholesale=180, retail=180
    - '180/pcs' -> wholesale=180, retail=180
    """
    if pd.isna(price_val):
        return None, None

    price_str = str(price_val).strip()

    # Handle ranges like "180/250"
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
            # First value = wholesale/workshop price, Second value = retail/normal price
            return numeric_parts[0], numeric_parts[1]
        elif len(numeric_parts) == 1:
            return numeric_parts[0], numeric_parts[0]

    # Handle single value
    try:
        cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
        if cleaned:
            price = float(cleaned)
            return price, price
    except:
        pass

    return None, None

def get_or_create_category(category_name):
    """Get category ID or create if doesn't exist"""
    if not category_name:
        category_name = 'Uncategorized'
    
    # Check if exists
    result = db.execute_query(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (category_name,)
    )
    if result:
        return result[0]['category_id']
    
    # Create new
    category_id = db.execute_insert(
        "INSERT INTO categories (category_name, description) VALUES (?, ?)",
        (category_name, f"Imported from {category_name} sheet")
    )
    print(f"    Created category: {category_name} (ID: {category_id})")
    return category_id

def get_or_create_brand(brand_name):
    """Get brand ID or create if doesn't exist"""
    if not brand_name:
        brand_name = 'Generic'
    
    brand_name = str(brand_name).strip().upper()
    
    # Check if exists
    result = db.execute_query(
        "SELECT brand_id FROM brands WHERE brand_name = ?",
        (brand_name,)
    )
    if result:
        return result[0]['brand_id']
    
    # Create new
    brand_id = db.execute_insert(
        "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
        (brand_name, f"Imported brand")
    )
    print(f"    Created brand: {brand_name} (ID: {brand_id})")
    return brand_id

def analyze_sheet_structure(df, sheet_name):
    """Find the header row in a sheet"""
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
        
        if any(keyword in row_str for keyword in ['company', 'items', 'bike', 'price', 'qty', 'stock', 'bikes names']):
            return idx
    return None

def extract_data_from_sheet(excel_file, sheet_name):
    """Extract product data from a specific sheet"""
    
    # Read without headers first
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    
    if len(df) < 2:
        return []
    
    # Find header row
    header_row_idx = analyze_sheet_structure(df, sheet_name)
    if header_row_idx is None:
        print(f"  Warning: Could not find header row in sheet '{sheet_name}'")
        return []
    
    # Read with proper headers
    df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row_idx)
    
    # Map columns
    column_mapping = {}
    for col in df_data.columns:
        col_str = str(col).lower().strip()
        
        # Product name mapping
        if any(k in col_str for k in ['company names', 'items', 'bike names', 'bikes names', 'bearing size', 'tyre sizes']):
            column_mapping[col] = 'product_name'
        # Company/Brand mapping
        elif any(k in col_str for k in ['company', 'brand']) and 'company names' not in col_str:
            column_mapping[col] = 'company'
        # Price mappings
        elif any(k in col_str for k in ['wholesale', 'w/s']):
            column_mapping[col] = 'wholesale_price'
        elif any(k in col_str for k in ['retail']):
            column_mapping[col] = 'retail_price'
        elif 'price' in col_str:
            column_mapping[col] = 'price'
        # Quantity mappings
        elif any(k in col_str for k in ['qty in hand', 'quantity in hand', 'stock']):
            column_mapping[col] = 'qty_in_hand'
        # Status
        elif 'status' in col_str:
            column_mapping[col] = 'status'
    
    # Remove duplicate mappings
    seen_targets = set()
    filtered_mapping = {}
    for source, target in column_mapping.items():
        if target not in seen_targets:
            filtered_mapping[source] = target
            seen_targets.add(target)
    
    df_data.rename(columns=filtered_mapping, inplace=True)
    
    products = []
    current_company = None
    
    for idx, row in df_data.iterrows():
        # Skip empty rows
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
        
        # Skip header repeat rows
        company_val = str(row.get('company', '')).strip()
        if company_val.upper() == sheet_name.upper():
            continue
        
        product = {
            'category': sheet_name,
            'brand': None,
            'product_name': None,
            'cost_price': None,      # wholesale
            'normal_price': None,    # retail
            'workshop_price': None,  # same as retail
            'stock': 0,
            'reorder_level': 10,
            'status': None
        }
        
        # Extract company/brand (carry forward if empty)
        if 'company' in df_data.columns:
            company = clean_value(row.get('company'))
            if company:
                current_company = company
            product['brand'] = current_company
        
        # Extract product name
        if 'product_name' in df_data.columns:
            product['product_name'] = clean_value(row.get('product_name'))
        
        # Skip if no product name
        if not product['product_name']:
            continue
        
        # Handle prices
        wholesale_price = None
        retail_price = None
        
        if 'wholesale_price' in df_data.columns:
            wp = clean_value(row.get('wholesale_price'))
            if wp:
                wholesale, retail = parse_price(wp)
                wholesale_price = wholesale  # workshop price
                retail_price = retail  # normal price
        
        if 'retail_price' in df_data.columns:
            rp = clean_value(row.get('retail_price'))
            if rp:
                _, retail = parse_price(rp)
                retail_price = retail  # normal price
        
        if 'price' in df_data.columns:
            price = clean_value(row.get('price'))
            if price:
                wholesale, retail = parse_price(price)
                if wholesale_price is None:
                    wholesale_price = wholesale  # workshop price
                if retail_price is None:
                    retail_price = retail  # normal price
        
        product['cost_price'] = wholesale_price or 0
        product['normal_price'] = retail_price or wholesale_price or 0
        product['workshop_price'] = product['normal_price']
        
        # Extract stock
        if 'qty_in_hand' in df_data.columns:
            try:
                qty = clean_value(row.get('qty_in_hand'))
                if qty:
                    product['stock'] = int(float(qty))
            except:
                product['stock'] = 0
        
        # Extract qty_sold if available
        if 'qty_sold' in df_data.columns:
            try:
                sold = clean_value(row.get('qty_sold'))
                if sold:
                    product['qty_sold'] = int(float(sold))
            except:
                product['qty_sold'] = 0
        else:
            product['qty_sold'] = 0
        
        # Calculate stock based on qty_in_hand and qty_sold
        # stock = initial quantity, qty_sold = total sold
        # available_stock will be computed as (stock - qty_sold)
        if product['stock'] < product['qty_sold']:
            # Ensure stock is at least qty_sold
            product['stock'] = product['qty_sold']
        
        products.append(product)
    
    return products

def import_product_to_db(product, category_id, brand_id):
    """Import a single product to the database"""
    try:
        # Generate SKU using the SKU generator
        sku = SKUGenerator.generate_sku(category_id, brand_id)
        product['sku'] = sku
        # Insert product
        product_id = db.execute_insert("""
            INSERT INTO products (
                name, sku, category_id, brand_id,
                description, stock, qty_sold, 
                price_normal, price_workshop, cost_price,
                reorder_level, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['product_name'],
            sku,
            category_id,
            brand_id,
            product['description'] if 'description' in product else f"Imported from {sheet_name}",
            product['stock'],
            product.get('qty_sold', 0),
            product['normal_price'],
            product['workshop_price'],
            product['cost_price'],
            product['reorder_level'],
            1  # is_active
        ))
        
        return product_id
    except Exception as e:
        print(f"    Error importing product '{product['product_name']}': {e}")
        return None

def main():
    excel_path = 'Diwan Autoparts backup.xlsx'
    
    print("=" * 80)
    print("EXCEL TO DATABASE IMPORT - Diwan Autoparts")
    print("=" * 80)
    
    if not os.path.exists(excel_path):
        print(f"\nError: File '{excel_path}' not found!")
        print("Please ensure the Excel file is in the same folder as this script.")
        return
    
    print(f"\nLoading Excel file: {excel_path}")
    
    try:
        excel_file = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    total_imported = 0
    total_skipped = 0
    categories_created = 0
    brands_created = 0
    
    for sheet_name in excel_file.sheet_names:
        if sheet_name in EXCLUDE_SHEETS or sheet_name.startswith('/'):
            print(f"\nSkipping sheet: '{sheet_name}' (excluded)")
            continue
        
        print(f"\nProcessing sheet: '{sheet_name}'...")
        
        try:
            products = extract_data_from_sheet(excel_file, sheet_name)
            
            if not products:
                print(f"  No products found in this sheet")
                continue
            
            print(f"  Found {len(products)} products")
            
            # Get or create category
            category_id = get_or_create_category(sheet_name)
            
            imported_count = 0
            for product in products:
                # Get or create brand
                brand_id = get_or_create_brand(product['brand'])
                
                # Import product
                product_id = import_product_to_db(product, category_id, brand_id)
                if product_id:
                    imported_count += 1
            
            print(f"  Imported {imported_count}/{len(products)} products")
            total_imported += imported_count
            total_skipped += (len(products) - imported_count)
            
        except Exception as e:
            print(f"  Error processing sheet: {e}")
            import traceback
            traceback.print_exc()
            total_skipped += 1
    
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total products imported: {total_imported}")
    print(f"Total products skipped: {total_skipped}")
    print("\nImport complete! You can now open your Inventory Management app.")

if __name__ == "__main__":
    main()
