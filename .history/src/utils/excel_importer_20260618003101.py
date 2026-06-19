"""
Simple Excel Importer for Diwan Autoparts
Browse → Preview → Import workflow
"""

import pandas as pd
import sys
import os
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from utils.sku_generator import SKUGenerator


class SimpleExcelImporter:
    """Simple Excel importer with browse → preview → import workflow"""
    
    COLUMN_MAPPINGS = {
        'company': ['Company', 'company', 'BRAND', 'Brand'],
        'bikes_names': ['Bikes names', 'Bikes Names', 'Bike Names', 'bike names', 'Items', 'items', 'Company names'],
        'wholesale_price': [
            'Wholesale Price',
            'Wholesale price',
            'wholesale price',
            'W/S Price',
            'W/S',
            # Observed variants:
            'Wholesale Price/SET',
            'Wholesale Price/PCS',
            'Wholesale Price / SET',
            'Wholesale Price / PCS',
            'Wholesale Price/ SET',
            'Wholesale Price/ PCS',
        ],
        # Excel header observed variants:
        # "Retail Price / Last Price"
        # and also "Retail Price/SET", "Retail Price/PCS" (with spacing differences)
        'retail_price': [
            'Retail Price',
            'Retail price',
            'retail price',
            'Retail Price / Last Price',
            'Retail Price/Last Price',
            'Retail Price /Last Price',
            'Retail Price/ Last Price',
            # Observed variants:
            'Retail Price/SET',
            'Retail Price/PCS',
            'Retail Price / SET',
            'Retail Price / PCS',
            'Retail Price/ SET',
            'Retail Price/ PCS',
        ],
        'qty_in_hand': ['Qty in Hand', 'Qty in hand', 'qty in hand', 'Stock', 'stock', 'Qty'],
        'qty_sold': ['Qty Sold', 'Qty sold', 'qty sold', 'Sold', 'sold', 'Quantity Sold']
    }
    
    EXCLUDE_SHEETS = ['Home', 'Home ', 'Dashboard', 'Sheet1', 'Daya form', '/']
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.file_path = None
        self.preview_data = []
        self.stats = {
            'sheets_processed': 0,
            'products_imported': 0,
            'categories_created': 0,
            'brands_created': 0,
            'errors': []
        }
    
    def browse_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            parent=self.parent,
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        return file_path if file_path else None
    
    def extract_preview_data(self, file_path):
        """Extract preview data from all sheets"""
        try:
            excel_file = pd.ExcelFile(file_path)
            preview = []
            
            for sheet_name in excel_file.sheet_names:
                if sheet_name in self.EXCLUDE_SHEETS or sheet_name.startswith('/'):
                    continue
                
                # Read sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                if len(df) < 3:
                    continue
                
                # Find header row
                header_row = self._find_header_row(df)
                if header_row is None:
                    continue
                
                # Read with headers
                df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)
                
                # Find columns
                company_col = self._find_column(df_data, 'company')
                bikes_col = self._find_column(df_data, 'bikes_names')
                wholesale_col = self._find_column(df_data, 'wholesale_price')
                retail_col = self._find_column(df_data, 'retail_price')
                qty_col = self._find_column(df_data, 'qty_in_hand')
                
                if not bikes_col:
                    continue
                
                # Extract first 5 products for preview
                products = []
                current_company = None
                count = 0
                
                for idx, row in df_data.iterrows():
                    if count >= 5:
                        break
                    
                    # Skip empty rows
                    try:
                        if row.isna().all():
                            continue
                    except:
                        pass
                    
                    # Get product name and ensure it's a string
                    raw_name = row.get(bikes_col)
                    if pd.isna(raw_name):
                        continue
                    product_name = str(raw_name).strip()
                    if not product_name or product_name.lower() == sheet_name.lower():
                        continue
                    
                    # Get company
                    brand = 'Generic'
                    if company_col:
                        company = row.get(company_col)
                        if pd.notna(company):
                            current_company = str(company).strip()
                        if current_company:
                            brand = current_company
                    
                    # Get prices
                    cost_price = 0
                    normal_price = 0
                    
                    if wholesale_col:
                        wp = row.get(wholesale_col)
                        if pd.notna(wp):
                            wholesale, retail = self._parse_price(wp)
                            cost_price = wholesale
                            normal_price = retail
                    
                    if retail_col:
                        rp = row.get(retail_col)
                        if pd.notna(rp):
                            _, normal_price = self._parse_price(rp)
                    
                    # Get stock
                    stock = 0
                    if qty_col:
                        try:
                            qty = row.get(qty_col)
                            if pd.notna(qty):
                                stock = int(float(qty))
                        except:
                            pass
                    
                    products.append({
                        'sheet': sheet_name,
                        'name': product_name,
                        'brand': brand,
                        'cost': cost_price,
                        'price': normal_price,
                        'stock': stock
                    })
                    count += 1
                
                if products:
                    preview.append({
                        'sheet_name': sheet_name,
                        'total_rows': len(df_data) - header_row - 1,
                        'sample_products': products
                    })
            
            return preview
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Excel file:\n{str(e)}")
            return None
    
    def import_file(self, file_path, progress_callback=None):
        """Import all data from Excel file"""
        try:
            excel_file = pd.ExcelFile(file_path)
            total_imported = 0
            
            for sheet_name in excel_file.sheet_names:
                if sheet_name in self.EXCLUDE_SHEETS or sheet_name.startswith('/'):
                    continue
                
                if progress_callback:
                    progress_callback(f"Processing: {sheet_name}...")
                
                # Get or create category
                category_id = self._get_or_create_category(sheet_name)
                
                # Process sheet
                imported = self._process_sheet(excel_file, sheet_name, category_id)
                total_imported += imported
                
                if progress_callback:
                    progress_callback(f"  ✓ Imported {imported} products")
            
            return total_imported
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Import failed:\n{str(e)}")
            return 0
    
    def _find_header_row(self, df):
        """Find header row in dataframe"""
        for idx in range(min(10, len(df))):
            row = df.iloc[idx]
            row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
            if any(k in row_str for k in ['company', 'bike', 'price', 'qty', 'stock', 'names']):
                return idx
        return None
    
    def _normalize_header(self, s):
        """Normalize Excel header text for matching."""
        import re
        return re.sub(r'\s+', ' ', str(s).strip().lower())

    def _find_column(self, df, field_name):
        """Find column by possible names (case/whitespace-insensitive)."""
        possible_names = self.COLUMN_MAPPINGS.get(field_name, [field_name])
        normalized_possible = {self._normalize_header(n) for n in possible_names}

        for col in df.columns:
            if self._normalize_header(col) in normalized_possible:
                return col
        return None
    
    def _clean_value(self, val):
        """Clean cell value"""
        if pd.isna(val):
            return None
        if isinstance(val, str):
            val = val.strip()
            if val == '':
                return None
        return val
    
    def _parse_price(self, price_val):
        """Parse price value, tolerating currency symbols and thousand separators."""
        if pd.isna(price_val):
            return 0, 0

        price_str = str(price_val).strip()
        if not price_str:
            return 0, 0

        def parse_one(part: str) -> float:
            import re
            # Keep digits, dot and comma; then normalize:
            # - Remove currency symbols / spaces
            # - Treat comma as thousand separator unless it looks like decimal separator
            s = str(part).strip()

            # Remove any currency text and spaces
            s = re.sub(r'[^\d,.\-]', '', s)
            if not s:
                return 0.0

            # If both comma and dot exist, assume comma is thousand sep.
            if ',' in s and '.' in s:
                s = s.replace(',', '')
            else:
                # If only commas exist, treat them as thousand separators.
                if ',' in s and '.' not in s:
                    s = s.replace(',', '')

            try:
                return float(s) if s else 0.0
            except:
                return 0.0

        if '/' in price_str:
            parts = price_str.split('/')
            nums = [parse_one(p) for p in parts if str(p).strip() != '']
            nums = [n for n in nums if n != 0.0 or len(nums) == 2]  # keep zeros if both parts present
            if len(nums) >= 2:
                return nums[0], nums[1]
            if len(nums) == 1:
                return nums[0], nums[0]

        p = parse_one(price_str)
        return p, p
    
    def _get_or_create_category(self, name):
        """Get or create category"""
        result = db.execute_query(
            "SELECT category_id FROM categories WHERE LOWER(category_name) = LOWER(?)",
            (name,)
        )
        if result:
            return result[0]['category_id']
        
        cat_id = db.execute_insert(
            "INSERT INTO categories (category_name, description) VALUES (?, ?)",
            (name, f"Imported from {name}")
        )
        self.stats['categories_created'] += 1
        return cat_id
    
    def _get_or_create_brand(self, name):
        """Get or create brand"""
        if not name:
            name = 'Generic'
        
        name = str(name).strip().upper()
        
        result = db.execute_query(
            "SELECT brand_id FROM brands WHERE LOWER(brand_name) = LOWER(?)",
            (name,)
        )
        if result:
            return result[0]['brand_id']
        
        brand_id = db.execute_insert(
            "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
            (name, "Imported from Excel")
        )
        self.stats['brands_created'] += 1
        return brand_id
    
    def _process_sheet(self, excel_file, sheet_name, category_id):
        """Process a single sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            if len(df) < 3:
                return 0
            
            header_row = self._find_header_row(df)
            if header_row is None:
                return 0
            
            df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)
            
            company_col = self._find_column(df_data, 'company')
            bikes_col = self._find_column(df_data, 'bikes_names')
            wholesale_col = self._find_column(df_data, 'wholesale_price')
            retail_col = self._find_column(df_data, 'retail_price')
            qty_col = self._find_column(df_data, 'qty_in_hand')
            qty_sold_col = self._find_column(df_data, 'qty_sold')
            
            if not bikes_col:
                return 0

            # Debug/help for "prices not importing" cases:
            # If wholesale/retail columns weren't detected, surface available headers.
            if wholesale_col is None or retail_col is None:
                available_headers = [str(c) for c in df_data.columns]
                self.stats['errors'].append(
                    f"Sheet '{sheet_name}': column detection failed. "
                    f"wholesale_col={wholesale_col}, retail_col={retail_col}. "
                    f"Available headers={available_headers[:25]}"
                )
            
            imported = 0
            current_company = None
            
            for idx, row in df_data.iterrows():
                try:
                    # Skip empty
                    try:
                        if row.isna().all():
                            continue
                    except:
                        pass
                    
                    product_name = self._clean_value(row.get(bikes_col))
                    if not product_name or str(product_name).strip().lower() == sheet_name.lower():
                        continue
                    
                    # Company/Brand
                    if company_col:
                        company = self._clean_value(row.get(company_col))
                        if company:
                            current_company = company
                    brand = current_company or 'Generic'
                    brand_id = self._get_or_create_brand(brand)
                    
                    # Prices
                    cost_price = 0
                    normal_price = 0
                    
                    if wholesale_col:
                        wp = self._clean_value(row.get(wholesale_col))
                        if wp:
                            wholesale, retail = self._parse_price(wp)
                            cost_price = wholesale
                            normal_price = retail
                    
                    if retail_col:
                        rp = self._clean_value(row.get(retail_col))
                        if rp:
                            _, normal_price = self._parse_price(rp)
                    
                    # Stock
                    stock = 0
                    if qty_col:
                        try:
                            qty = self._clean_value(row.get(qty_col))
                            if qty:
                                stock = int(float(qty))
                        except:
                            pass
                    
                    # Qty Sold
                    qty_sold = 0
                    if qty_sold_col:
                        try:
                            sold = self._clean_value(row.get(qty_sold_col))
                            if sold:
                                qty_sold = int(float(sold))
                        except:
                            pass
                    
                    # Generate SKU
                    sku = SKUGenerator.generate_sku(category_id, brand_id)
                    
                    # Insert product
                    # Semantics:
                    # - retail/normal -> price_normal
                    # - wholesale/workshop -> price_workshop (and also cost_price)
                    db.execute_insert("""
                        INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,
                                            price_normal, price_workshop, cost_price, reorder_level, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (product_name, sku, category_id, brand_id, stock, qty_sold,
                          normal_price, cost_price, cost_price, 10, 1))
                    
                    imported += 1
                    
                except Exception as e:
                    self.stats['errors'].append(f"Row {idx}: {str(e)}")
                    continue
            
            self.stats['sheets_processed'] += 1
            return imported
            
        except Exception as e:
            self.stats['errors'].append(f"Sheet {sheet_name}: {str(e)}")
            return 0
