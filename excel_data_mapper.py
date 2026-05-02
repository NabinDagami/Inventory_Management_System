"""
Excel Data Mapper for Diwan Autoparts
Maps data from Excel sheets to structured format for database import
"""

import pandas as pd
import json
from pathlib import Path

# Sheets to exclude (non-data sheets)
EXCLUDE_SHEETS = ['Home', 'Home ', 'Dashboard', 'Sheet1', 'Daya form']

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
    Extract numeric price from various formats like '180/250', '180', '180/pcs'
    Returns: (workshop_price, normal_price)
    - For 'X/Y' format: X = workshop_price (wholesale), Y = normal_price (retail)
    - For single value: Both = value
    """
    if pd.isna(price_val):
        return None, None

    price_str = str(price_val).strip()

    # Handle ranges like "180/250" - first = wholesale (workshop), second = retail (normal)
    if '/' in price_str:
        parts = price_str.split('/')
        # Filter out non-numeric parts (like 'pcs')
        numeric_parts = []
        for part in parts:
            try:
                # Remove any non-numeric characters except decimal point
                cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                if cleaned:
                    numeric_parts.append(float(cleaned))
            except:
                pass
        if len(numeric_parts) >= 2:
            # First value = wholesale/workshop, Second value = retail/normal
            return numeric_parts[0], numeric_parts[1]
        elif len(numeric_parts) == 1:
            # Single value in X/Y format - use for both
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

def analyze_sheet_structure(df, sheet_name):
    """Analyze the structure of a sheet and identify column mappings"""
    structure = {
        'sheet_name': sheet_name,
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'header_row': None,
        'columns': {}
    }

    # Find the header row (usually contains key column names)
    for idx in range(min(5, len(df))):
        row = df.iloc[idx]
        row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])

        if any(keyword in row_str for keyword in ['company', 'items', 'bike', 'price', 'qty', 'stock']):
            structure['header_row'] = idx
            break

    return structure

def extract_data_from_sheet(excel_file, sheet_name):
    """Extract product data from a specific sheet"""

    # Read the sheet without headers first
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

    if len(df) < 2:
        return []

    # Analyze structure
    structure = analyze_sheet_structure(df, sheet_name)

    if structure['header_row'] is None:
        print(f"  Warning: Could not find header row in sheet '{sheet_name}'")
        return []

    header_row_idx = structure['header_row']

    # Get headers
    headers = df.iloc[header_row_idx].tolist()
    headers = [str(h).strip().lower() if pd.notna(h) else f'col_{i}' for i, h in enumerate(headers)]

    # Read again with proper headers
    df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row_idx)

    # Rename columns to standardized names for easier processing
    column_mapping = {}
    for i, col in enumerate(df_data.columns):
        col_str = str(col).lower().strip()

        # Product/Bike name mapping - check first to avoid matching 'company' before 'company names'
        if any(k in col_str for k in ['company names', 'items', 'bike names', 'bikes names', 'bearing size', 'tyre sizes']):
            column_mapping[col] = 'product_name'

        # Company/Brand mapping
        elif any(k in col_str for k in ['company', 'brand']) and 'company names' not in col_str:
            column_mapping[col] = 'company'

        # Generic product name mapping
        elif any(k in col_str for k in ['names', 'sizes', 'product']):
            column_mapping[col] = 'product_name'

        # Wholesale price mapping
        elif any(k in col_str for k in ['wholesale', 'w/s']):
            column_mapping[col] = 'wholesale_price'

        # Retail price mapping
        elif any(k in col_str for k in ['retail']):
            column_mapping[col] = 'retail_price'

        # Generic price mapping (when only one price column)
        elif 'price' in col_str and 'wholesale' not in col_str and 'retail' not in col_str:
            column_mapping[col] = 'price'

        # Quantity in hand mapping
        elif any(k in col_str for k in ['qty in hand', 'quantity in hand', 'stock']):
            column_mapping[col] = 'qty_in_hand'

        # Quantity sold mapping
        elif any(k in col_str for k in ['qty sold', 'quantity sold']):
            column_mapping[col] = 'qty_sold'

        # Available stock mapping
        elif any(k in col_str for k in ['available']):
            column_mapping[col] = 'available_stock'

        # Status mapping
        elif 'status' in col_str:
            column_mapping[col] = 'status'

    # Rename columns - handle duplicates by keeping only the first occurrence
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
        # Skip empty rows - check if all values in the row are NaN
        try:
            if row.isna().all():
                continue
        except:
            # If we can't check with isna().all(), try alternative approach
            all_empty = True
            for val in row.values:
                if pd.notna(val):
                    all_empty = False
                    break
            if all_empty:
                continue

        product = {
            'category': sheet_name,
            'sub_category': None,
            'brand': None,
            'sub_brand': None,
            'product_name': None,
            'wholesale_price': None,
            'retail_price': None,
            'qty_in_hand': 0,
            'qty_sold': 0,
            'available_stock': 0,
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

        # Handle price columns
        wholesale_price = None
        retail_price = None

        if 'wholesale_price' in df_data.columns:
            wp = clean_value(row.get('wholesale_price'))
            if wp:
                ws, rt = parse_price(wp)
                wholesale_price = ws  # workshop price
                if retail_price is None:
                    retail_price = rt  # normal price (if not already set)

        if 'retail_price' in df_data.columns:
            rp = clean_value(row.get('retail_price'))
            if rp:
                ws, rt = parse_price(rp)
                retail_price = rt  # normal price
                if wholesale_price is None:
                    wholesale_price = ws  # workshop price (if not already set)

        if 'price' in df_data.columns:
            price = clean_value(row.get('price'))
            if price:
                ws, rt = parse_price(price)
                if wholesale_price is None:
                    wholesale_price = ws  # workshop price
                if retail_price is None:
                    retail_price = rt  # normal price

        product['wholesale_price'] = wholesale_price
        product['retail_price'] = retail_price

        # Extract quantities
        if 'qty_in_hand' in df_data.columns:
            try:
                product['qty_in_hand'] = int(float(clean_value(row.get('qty_in_hand')) or 0))
            except:
                product['qty_in_hand'] = 0

        if 'qty_sold' in df_data.columns:
            try:
                product['qty_sold'] = int(float(clean_value(row.get('qty_sold')) or 0))
            except:
                product['qty_sold'] = 0

        if 'available_stock' in df_data.columns:
            try:
                product['available_stock'] = int(float(clean_value(row.get('available_stock')) or 0))
            except:
                product['available_stock'] = 0

        # Extract status
        if 'status' in df_data.columns:
            product['status'] = clean_value(row.get('status'))

        # Only add if we have a product name
        if product['product_name']:
            products.append(product)

    return products

def map_excel_to_database(excel_path):
    """Main function to map Excel data to database structure"""

    print(f"Loading Excel file: {excel_path}")
    excel_file = pd.ExcelFile(excel_path)

    all_products = []
    summary = {
        'total_sheets': len(excel_file.sheet_names),
        'data_sheets': [],
        'excluded_sheets': [],
        'products_by_category': {}
    }

    for sheet_name in excel_file.sheet_names:
        if sheet_name in EXCLUDE_SHEETS:
            summary['excluded_sheets'].append(sheet_name)
            continue

        print(f"\nProcessing sheet: '{sheet_name}'...")
        summary['data_sheets'].append(sheet_name)

        try:
            products = extract_data_from_sheet(excel_file, sheet_name)
            all_products.extend(products)
            summary['products_by_category'][sheet_name] = len(products)
            print(f"  Extracted {len(products)} products")
        except Exception as e:
            print(f"  Error processing sheet: {e}")
            summary['products_by_category'][sheet_name] = 0

    # Generate summary
    summary['total_products'] = len(all_products)

    return all_products, summary

def export_to_json(products, output_path='mapped_products.json'):
    """Export mapped products to JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"\nExported {len(products)} products to {output_path}")

def export_to_sql(products, output_path='import_products.sql'):
    """Generate SQL INSERT statements"""

    sql_lines = [
        "-- SQL Import Script for Diwan Autoparts Products",
        "-- Generated from Excel mapping",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]

    # Create categories table insert (unique categories)
    categories = list(set(p['category'] for p in products if p['category']))
    sql_lines.append("-- Insert Categories")
    for cat in categories:
        safe_cat = cat.replace("'", "''")
        sql_lines.append(f"INSERT OR IGNORE INTO categories (name) VALUES ('{safe_cat}');")
    sql_lines.append("")

    # Create brands table insert (unique brands)
    brands = list(set(p['brand'] for p in products if p['brand']))
    sql_lines.append("-- Insert Brands")
    for brand in brands:
        safe_brand = brand.replace("'", "''")
        sql_lines.append(f"INSERT OR IGNORE INTO brands (name) VALUES ('{safe_brand}');")
    sql_lines.append("")

    # Create products table insert
    sql_lines.append("-- Insert Products")
    sql_lines.append("""INSERT INTO products (
    category, sub_category, brand, sub_brand, product_name,
    wholesale_price, retail_price, qty_in_hand, qty_sold,
    available_stock, status
) VALUES""")

    value_lines = []
    for p in products:
        cat = str(p['category'] or '').replace("'", "''")
        sub_cat = str(p['sub_category'] or '').replace("'", "''")
        brand = str(p['brand'] or '').replace("'", "''")
        sub_brand = str(p['sub_brand'] or '').replace("'", "''")
        prod_name = str(p['product_name'] or '').replace("'", "''")
        status = str(p['status'] or '').replace("'", "''")

        values = (
            f"'{cat}'",
            f"'{sub_cat}'",
            f"'{brand}'",
            f"'{sub_brand}'",
            f"'{prod_name}'",
            str(p['wholesale_price'] or 'NULL'),
            str(p['retail_price'] or 'NULL'),
            str(p['qty_in_hand']),
            str(p['qty_sold']),
            str(p['available_stock']),
            f"'{status}'"
        )
        value_lines.append(f"    ({', '.join(values)})")

    sql_lines.append(",\n".join(value_lines) + ";")
    sql_lines.append("")
    sql_lines.append("COMMIT;")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    print(f"Exported SQL to {output_path}")

def main():
    excel_path = 'Diwan Autoparts backup.xlsx'

    print("=" * 80)
    print("EXCEL DATA MAPPER - Diwan Autoparts")
    print("=" * 80)

    # Map the data
    products, summary = map_excel_to_database(excel_path)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sheets in Excel: {summary['total_sheets']}")
    print(f"Data sheets processed: {len(summary['data_sheets'])}")
    print(f"Excluded sheets: {', '.join(summary['excluded_sheets'])}")
    print(f"\nTotal products extracted: {summary['total_products']}")
    print("\nProducts by category:")
    for cat, count in sorted(summary['products_by_category'].items()):
        print(f"  - {cat}: {count} products")

    # Export to JSON
    export_to_json(products, 'mapped_products.json')

    # Export to SQL
    export_to_sql(products, 'import_products.sql')

    # Print sample data
    print("\n" + "=" * 80)
    print("SAMPLE PRODUCTS (First 5)")
    print("=" * 80)
    for i, p in enumerate(products[:5]):
        print(f"\n{i+1}. {p['product_name']}")
        print(f"   Category: {p['category']}")
        print(f"   Brand: {p['brand']}")
        print(f"   Prices: Wholesale={p['wholesale_price']}, Retail={p['retail_price']}")
        print(f"   Stock: {p['qty_in_hand']} (Available: {p['available_stock']})")
        print(f"   Status: {p['status']}")

    return products, summary

if __name__ == "__main__":
    products, summary = main()
