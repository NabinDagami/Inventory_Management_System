"""
Robust Data Import System for Diwan Autoparts
Ensures strict structural integrity and data mapping accuracy
"""

import pandas as pd
import numpy as np
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import traceback

class DataImportValidator:
    """
    Validates Excel data against database schema with strict integrity checks
    """
    
    def __init__(self):
        # Database schema definition
        self.db_schema = {
            'products': {
                'required_fields': {
                    'name': {'type': 'string', 'max_length': 200, 'nullable': False},
                    'sku': {'type': 'string', 'max_length': 50, 'nullable': False, 'unique': True},
                    'price_normal': {'type': 'decimal', 'precision': (10, 2), 'nullable': False},
                    'price_workshop': {'type': 'decimal', 'precision': (10, 2), 'nullable': False},
                    'cost_price': {'type': 'decimal', 'precision': (10, 2), 'nullable': False},
                },
                'optional_fields': {
                    'category': {'type': 'string', 'max_length': 100, 'nullable': True},
                    'brand': {'type': 'string', 'max_length': 100, 'nullable': True},
                    'description': {'type': 'text', 'nullable': True},
                    'stock': {'type': 'integer', 'min_value': 0, 'nullable': False, 'default': 0},
                    'qty_sold': {'type': 'integer', 'min_value': 0, 'nullable': False, 'default': 0},
                    'available_stock': {'type': 'integer', 'min_value': 0, 'nullable': True, 'computed': True},
                    'reorder_level': {'type': 'integer', 'min_value': 0, 'nullable': False, 'default': 10},
                    'is_active': {'type': 'boolean', 'nullable': False, 'default': True},
                },
                'computed_fields': ['available_stock'],
                'foreign_keys': {
                    'category_id': 'categories',
                    'brand_id': 'brands',
                }
            },
            'categories': {
                'required_fields': {
                    'category_name': {'type': 'string', 'max_length': 100, 'nullable': False, 'unique': True},
                },
                'optional_fields': {
                    'description': {'type': 'text', 'nullable': True},
                }
            },
            'brands': {
                'required_fields': {
                    'brand_name': {'type': 'string', 'max_length': 100, 'nullable': False, 'unique': True},
                },
                'optional_fields': {
                    'description': {'type': 'text', 'nullable': True},
            }}
        }
        
        # Excel column mapping patterns
        self.column_patterns = {
            'name': [
                r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', 
                r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'
            ],
            'sku': [
                r'^sku$', r'^code$', r'product.*code',
            ],
            'category': [
                r'^category$', r'^type$',
            ],
            'brand': [
                r'^brand$', r'^company$', r'^manufacturer$',
            ],
            'stock': [
                r'^qty.*hand$', r'^stock$', r'^quantity$', r'^available.*stock$',
            ],
            'qty_sold': [
                r'^qty.*sold$', r'^sold$',
            ],
            'price_normal': [
                r'^retail.*', r'^price.*', r'^normal.*',
            ],
            'price_workshop': [
                r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*',
            ],
            'cost_price': [
                r'^cost.*price$', r'^purchase.*price$',
            ],
            'reorder_level': [
                r'^reorder.*level$', r'^min.*stock$',
            ],
            'description': [
                r'^description$',
            ],
            'status': [
                r'^status$',
            ]
        }
        
        # Validation errors
        self.errors = []
        self.warnings = []
        
    def validate_excel_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive Excel file validation
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Check file exists
            if not pd.io.common.file_exists(file_path):
                return {'valid': False, 'errors': [f'File not found: {file_path}']}
            
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            
            result = {
                'file_path': file_path,
                'sheets': [],
                'total_sheets': len(excel_file.sheet_names),
                'valid': True,
                'errors': [],
                'warnings': [],
                'sheet_details': []
            }
            
            excluded_sheets = ['Home', 'Dashboard', 'Sheet1', 'Daya form', '/', '']
            
            for sheet_name in excel_file.sheet_names:
                if any(excluded in sheet_name for excluded in excluded_sheets):
                    continue
                
                sheet_result = self._validate_sheet(excel_file, sheet_name)
                result['sheet_details'].append(sheet_result)
                # DEBUG: Show column mapping
                if sheet_result.get("column_mapping") and len(sheet_result["column_mapping"]) > 0:
                    print(f"  MAPPED {sheet_name}: {sheet_result['column_mapping']}")

                
                if not sheet_result['valid']:
                    result['valid'] = False
                    result['errors'].extend(sheet_result['errors'])
                
                result['warnings'].extend(sheet_result.get('warnings', []))
            
            result['errors'] = self.errors
            result['warnings'] = self.warnings
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Error reading Excel file: {str(e)}'],
                'warnings': []
            }
    
    def _validate_sheet(self, excel_file: pd.ExcelFile, sheet_name: str) -> Dict[str, Any]:
        """
        Validate individual sheet structure and data
        """
        print(f"  [VALIDATE_SHEET] Processing: {sheet_name}")
        sheet_result = {
            'sheet_name': sheet_name,
            'valid': True,
            'errors': [],
            'warnings': [],
            'columns': [],
            'row_count': 0,
            'column_mapping': {},
            'data_sample': []
        }
        
        try:
            # Read sheet without headers first
            df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            
            if len(df_raw) < 2:
                sheet_result['errors'].append(f'Sheet has insufficient data')
                sheet_result['valid'] = False
                return sheet_result
            
            # Find header row
            header_row_idx = self._find_header_row(df_raw)
            
            if header_row_idx is None:
                sheet_result['errors'].append('Could not identify header row')
                sheet_result['valid'] = False
                return sheet_result
            
            # Read with headers
            df_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row_idx)
            
            sheet_result['row_count'] = len(df_data)
            sheet_result['header_row'] = header_row_idx
            
            # Clean column names
            df_data.columns = [self._clean_column_name(col) for col in df_data.columns]
            
            # Map columns to database fields
            column_mapping = self._map_columns(df_data.columns.tolist())
            sheet_result['column_mapping'] = column_mapping
            
            # Validate required fields
            
            # DEBUG
            if column_mapping:
                print(f"  [DEBUG] Mapped {len(column_mapping)} fields for {sheet_name}: {list(column_mapping.keys())}")
            
            # Validate required fields
            required_mapped = [v for k, v in column_mapping.items() 
                             if k in self.db_schema['products']['required_fields']]
            
            # Check for critical required fields
            critical_fields = ['name', 'cost_price', 'price_normal', 'price_workshop']
            for field in critical_fields:
                if field not in required_mapped:
                    sheet_result['errors'].append(
                        f'Missing required field: {field}'
                    )
                    sheet_result['valid'] = False
            
            # Validate data types and integrity
            field_errors = self._validate_data_integrity(df_data, column_mapping)
            sheet_result['errors'].extend(field_errors)
            
            if field_errors:
                sheet_result['valid'] = False
            
            # Check for empty data rows
            empty_rows = self._check_empty_rows(df_data, column_mapping)
            if empty_rows:
                sheet_result['warnings'].append(
                    f'Found {empty_rows} rows with insufficient data'
                )
            
            # Sample data
            sheet_result['data_sample'] = self._get_data_sample(df_data, column_mapping)
            
            sheet_result['columns'] = df_data.columns.tolist()
            
            if sheet_result['errors']:
                sheet_result['valid'] = False
            
            return sheet_result
            
        except Exception as e:
            sheet_result['errors'].append(f'Error processing sheet: {str(e)}')
            sheet_result['valid'] = False
            return sheet_result
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """
        Find the header row index by analyzing cell content patterns
        """
        for idx in range(min(10, len(df))):
            row = df.iloc[idx]
            row_str = ' '.join([str(x).lower().strip() for x in row if pd.notna(x)])
            
            # Look for key header indicators
            header_indicators = [
                'name', 'price', 'cost', 'sku', 'category', 'brand',
                'stock', 'qty', 'product'
            ]
            
            matches = sum(1 for indicator in header_indicators if indicator in row_str)
            
            if matches >= 2:  # At least 2 header indicators
                return idx
        
        return None
    
    def _clean_column_name(self, col_name: Any) -> str:
        """
        Clean and standardize column names
        """
        if pd.isna(col_name):
            return ''
        
        name = str(col_name).strip()
        name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        return name.lower().strip()
    
    def _map_columns(self, excel_columns: List[str]) -> Dict[str, str]:
        """
        Map Excel columns to database fields using pattern matching
        """
        mapping = {}
        
        for db_field, patterns in self.column_patterns.items():
            for excel_col in excel_columns:
                for pattern in patterns:
                    if re.search(pattern, excel_col, re.IGNORECASE):
                        if db_field not in mapping:
                            mapping[db_field] = excel_col
                            break
        
        return mapping
    
    def _validate_data_integrity(self, df: pd.DataFrame, mapping: Dict[str, str]) -> List[str]:
        """
        Validate data types and integrity for mapped columns
        """
        errors = []
        
        # Check each mapped field
        for db_field, excel_col in mapping.items():
            if excel_col not in df.columns:
                continue
            
            field_schema = None
            if db_field in self.db_schema['products']['required_fields']:
                field_schema = self.db_schema['products']['required_fields'][db_field]
            elif db_field in self.db_schema['products']['optional_fields']:
                field_schema = self.db_schema['products']['optional_fields'][db_field]
            
            if not field_schema:
                continue
            
            # Validate based on field type
            if field_schema['type'] == 'string':
                errors.extend(self._validate_string_field(df[excel_col], db_field, field_schema, excel_col))
            
            elif field_schema['type'] == 'number':
                errors.extend(self._validate_number_field(df[excel_col], db_field, field_schema, excel_col))
            
            elif field_schema['type'] == 'integer':
                errors.extend(self._validate_integer_field(df[excel_col], db_field, field_schema, excel_col))
            
            elif field_schema['type'] == 'decimal':
                errors.extend(self._validate_decimal_field(df[excel_col], db_field, field_schema, excel_col))
        
        # Check price relationships
        if 'price_workshop' in mapping and 'price_normal' in mapping:
            errors.extend(self._validate_price_relationship(
                df, mapping['price_workshop'], mapping['price_normal']
            ))
        
        # Check stock relationships
        if 'stock' in mapping and 'qty_sold' in mapping:
            if 'qty_sold' in mapping:
                errors.extend(self._validate_stock_relationship(
                    df, mapping['stock'], mapping['qty_sold']
                ))
        
        return errors
    
    def _validate_string_field(self, series: pd.Series, field_name: str, schema: Dict, excel_col: str) -> List[str]:
        """
        Validate string fields
        """
        errors = []
        
        # Check for nulls in required fields
        if not schema.get('nullable', True):
            null_count = series.isna().sum()
            if null_count > 0:
                errors.append(
                    f'Required field "{field_name}" ({excel_col}) has {null_count} empty values'
                )
        
        # Check max length
        max_length = schema.get('max_length')
        if max_length:
            long_values = series.dropna().astype(str).str.len() > max_length
            if long_values.any():
                count = long_values.sum()
                errors.append(
                    f'Field "{field_name}" ({excel_col}) has {count} values exceeding {max_length} characters'
                )
        
        return errors
    
    def _validate_number_field(self, series: pd.Series, field_name: str, schema: Dict, excel_col: str) -> List[str]:
        """
        Validate numeric fields
        """
        errors = []
        
        # Try to convert to numeric
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # Check for invalid numbers
        invalid_count = numeric_series.isna().sum() - series.isna().sum()
        if invalid_count > 0:
            errors.append(
                f'Field "{field_name}" ({excel_col}) has {invalid_count} non-numeric values'
            )
        
        # Check for negative values
        if (numeric_series < 0).any():
            errors.append(
                f'Field "{field_name}" ({excel_col}) has negative values'
            )
        
        return errors
    
    def _validate_integer_field(self, series: pd.Series, field_name: str, schema: Dict, excel_col: str) -> List[str]:
        """
        Validate integer fields
        """
        errors = []
        
        # Try to convert to integer
        int_series = pd.to_numeric(series, errors='coerce')
        
        # Check for non-integers
        non_int = int_series.dropna() % 1 != 0
        if non_int.any():
            errors.append(
                f'Field "{field_name}" ({excel_col}) has non-integer values'
            )
        
        # Check min value
        min_value = schema.get('min_value', 0)
        if (int_series < min_value).any():
            errors.append(
                f'Field "{field_name}" ({excel_col}) has values below minimum ({min_value})'
            )
        
        return errors
    
    def _validate_decimal_field(self, series: pd.Series, field_name: str, schema: Dict, excel_col: str) -> List[str]:
        """
        Validate decimal fields (prices)
        """
        errors = []
        
        # Parse prices with X/Y format
        parsed_prices = series.apply(lambda x: self._parse_price_value(x))
        
        # Check for invalid prices
        invalid_count = parsed_prices.apply(lambda x: x[0] is None and x[1] is None).sum()
        if invalid_count > 0:
            errors.append(
                f'Field "{field_name}" ({excel_col}) has {invalid_count} unparseable price values'
            )
        
        # Check for negative prices
        has_negative = parsed_prices.apply(lambda x: (x[0] is not None and x[0] < 0) or (x[1] is not None and x[1] < 0)).any()
        if has_negative:
            errors.append(
                f'Field "{field_name}" ({excel_col}) has negative price values'
            )
        
        return errors
    
    def _parse_price_value(self, value: Any) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse a price value that may be in X/Y format or single value
        Returns: (workshop_price, normal_price)
        """
        if pd.isna(value):
            return None, None
        
        price_str = str(value).strip()
        
        # Handle X/Y format
        if '/' in price_str:
            parts = price_str.split('/')
            prices = []
            for part in parts:
                try:
                    cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                    if cleaned:
                        prices.append(float(cleaned))
                except ValueError:
                    continue
            
            if len(prices) >= 2:
                return prices[0], prices[1]
            elif len(prices) == 1:
                return prices[0], prices[0]
        
        # Handle single value
        try:
            cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
            if cleaned:
                price = float(cleaned)
                return price, price
        except ValueError:
            pass
        
        return None, None
    
    def _validate_price_relationship(self, df: pd.DataFrame, workshop_col: str, normal_col: str) -> List[str]:
        """
        Validate that workshop price is typically less than normal price
        """
        errors = []
        
        # Parse both columns
        workshop_prices = df[workshop_col].apply(lambda x: self._parse_price_value(x)[0])
        normal_prices = df[normal_col].apply(lambda x: self._parse_price_value(x)[1])
        
        # Check for cases where workshop > normal
        invalid_prices = (workshop_prices > normal_prices) & workshop_prices.notna() & normal_prices.notna()
        
        if invalid_prices.any():
            count = invalid_prices.sum()
            errors.append(
                f'Found {count} products where workshop price exceeds normal price'
            )
        
        return errors
    
    def _validate_stock_relationship(self, df: pd.DataFrame, stock_col: str, sold_col: str) -> List[str]:
        """
        Validate that qty_sold doesn't exceed stock
        """
        errors = []
        
        stock_values = pd.to_numeric(df[stock_col], errors='coerce').fillna(0).astype(int)
        sold_values = pd.to_numeric(df[sold_col], errors='coerce').fillna(0).astype(int)
        
        # Check if qty_sold > stock
        invalid = sold_values > stock_values
        
        if invalid.any():
            count = invalid.sum()
            errors.append(
                f'Found {count} products where qty_sold exceeds available stock'
            )
        
        return errors
    
    def _check_empty_rows(self, df: pd.DataFrame, mapping: Dict[str, str]) -> int:
        """
        Check for rows with insufficient data
        """
        # Consider a row empty if critical fields are missing
        critical_fields = [mapping.get(f) for f in ['name', 'cost_price'] if f in mapping]
        
        if not critical_fields:
            return 0
        
        empty_count = 0
        for _, row in df.iterrows():
            if all(pd.isna(row.get(col)) for col in critical_fields):
                empty_count += 1
        
        return empty_count
    
    def _get_data_sample(self, df: pd.DataFrame, mapping: Dict[str, str], sample_size: int = 5) -> List[Dict]:
        """
        Get a sample of the data with mapped fields
        """
        sample = []
        
        for _, row in df.head(sample_size).iterrows():
            item = {}
            for db_field, excel_col in mapping.items():
                if excel_col in df.columns:
                    item[db_field] = row.get(excel_col)
            sample.append(item)
        
        return sample


class RobustDataImporter:
    """
    Robust data importer with validation and error handling
    """
    
    def __init__(self):
        self.validator = DataImportValidator()
        self.import_results = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'warnings': []
        }
    
    def import_from_excel(self, file_path: str, validate_only: bool = False) -> Dict[str, Any]:
        """
        Import data from Excel with full validation
        """
        print("=" * 80)
        print("ROBUST DATA IMPORT PROCESS")
        print("=" * 80)
        
        # Step 1: Validate structure
        print("\n[Step 1] Validating Excel file structure...")
        validation = self.validator.validate_excel_structure(file_path)
        
        if not validation['valid']:
            print(f"  [FAIL] Validation failed with {len(validation['errors'])} errors:")
            for error in validation['errors'][:5]:
                print(f"    - {error}")
            if len(validation['errors']) > 5:
                print(f"    ... and {len(validation['errors']) - 5} more errors")
            return validation
        
        print(f"  [OK] File structure is valid")
        print(f"  [OK] Found {validation['total_sheets']} sheets")
        
        for sheet in validation['sheet_details']:
            status = '[OK]' if sheet['valid'] else '[FAIL]'
            print(f"    {status} {sheet['sheet_name']}: {sheet['row_count']} rows")
            
            if not sheet['valid']:
                for error in sheet['errors']:
                    print(f"      - {error}")
        
        # Report warnings
        if validation['warnings']:
            print(f"\n  [WARN] Warnings: {len(validation['warnings'])}")
            for warning in validation['warnings'][:5]:
                print(f"    - {warning}")
        
        # Step 2: Preview mapped data
        print("\n[Step 2] Verifying column mappings...")
        total_mapped = 0
        for sheet in validation['sheet_details']:
            if sheet['valid'] and sheet['column_mapping']:
                print(f"  {sheet['sheet_name']}:")
                for db_field, excel_col in sheet['column_mapping'].items():
                    print(f"    {excel_col} -> {db_field}")
                total_mapped += len(sheet['column_mapping'])
        
        print("  Sheet details count: {}".format(len(validation["sheet_details"])))
        for s in validation["sheet_details"][:3]:
            print("    {}: valid={}, mappings={}".format(s["sheet_name"], s["valid"], len(s.get("column_mapping", {}))))
            if s.get("column_mapping"):
                print("      Mappings: {}".format(s["column_mapping"]))
        print(f"  [OK] Total fields mapped: {total_mapped}")
        
        # Step 3: Data sample
        print("\n[Step 3] Data sample verification...")
        for sheet in validation['sheet_details']:
            if sheet['valid'] and sheet['data_sample']:
                print(f"  {sheet['sheet_name']} (first row):")
                if sheet['data_sample']:
                    sample = sheet['data_sample'][0]
                    for field, value in list(sample.items())[:5]:
                        print(f"    {field}: {value}")
        
        # Step 4: Validate against database schema
        print("\n[Step 4] Validating against database schema...")
        
        if validate_only:
            print("  [PAUSE]  Validation only (no import)")
            return {
                'valid': True,
                'message': 'Validation passed',
                'validation': validation
            }
        
        # Step 5: Import data
        print("\n[Step 5] Importing data to database...")
        
        from src.models.database import db
        
        imported_count = 0
        error_count = 0
        
        for sheet in validation['sheet_details']:
            if not sheet['valid']:
                continue
            
            try:
                # Read sheet data
                excel_file = pd.ExcelFile(file_path)
                df = pd.read_excel(excel_file, sheet_name=sheet['sheet_name'])
                
                # Clean column names
                df.columns = [self.validator._clean_column_name(col) for col in df.columns]
                
                mapping = sheet['column_mapping']
                
                # Import each row
                for idx, row in df.iterrows():
                    try:
                        # Skip empty rows
                        if self._is_row_empty(row, mapping):
                            continue
                        
                        # Prepare product data
                        product_data = self._prepare_product_data(row, mapping, sheet['sheet_name'])
                        
                        # Get or create category
                        category_id = self._get_or_create_category(sheet['sheet_name'])
                        
                        # Get or create brand
                        brand_id = self._get_or_create_brand(product_data.get('brand', 'Generic'))
                        
                        # Generate SKU
                        from utils.sku_generator import SKUGenerator
                        sku = SKUGenerator.generate_sku(category_id, brand_id)
                        
                        # Calculate available_stock
                        stock = product_data.get('stock', 0)
                        qty_sold = product_data.get('qty_sold', 0)
                        available_stock = max(0, stock - qty_sold)
                        
                        # Insert product
                        db.execute_insert("""
                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold, available_stock,
                                                price_normal, price_workshop, cost_price, reorder_level, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            product_data['name'][:200],
                            sku,
                            category_id,
                            brand_id,
                            stock,
                            qty_sold,
                            available_stock,
                            product_data.get('price_normal', 0),
                            product_data.get('price_workshop', 0),
                            product_data.get('cost_price', 0),
                            product_data.get('reorder_level', 10),
                            1
                        ))
                        
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        print(f"    Row {idx}: {str(e)}")
                
                print(f"  [OK] {sheet['sheet_name']}: {imported_count} products imported")
                
            except Exception as e:
                print(f"  [FAIL] Error importing {sheet['sheet_name']}: {str(e)}")
                error_count += 1
        
        print(f"\n[Summary]")
        print(f"  Total imported: {imported_count}")
        print(f"  Errors: {error_count}")
        
        return {
            'valid': True,
            'imported': imported_count,
            'errors': error_count,
            'validation': validation
        }
    
    def _is_row_empty(self, row: pd.Series, mapping: Dict[str, str]) -> bool:
        """
        Check if row has critical data
        """
        critical_fields = ['name', 'cost_price']
        for field in critical_fields:
            if field in mapping and pd.notna(row.get(mapping[field])):
                return False
        return True
    
    def _prepare_product_data(self, row: pd.Series, mapping: Dict[str, str], sheet_name: str) -> Dict[str, Any]:
        """
        Extract and prepare product data from row
        """
        data = {}
        
        # Name
        name_col = mapping.get('name')
        if name_col and pd.notna(row.get(name_col)):
            data['name'] = str(row[name_col]).strip()
        else:
            data['name'] = f"Product from {sheet_name}"
        
        # Brand
        brand_col = mapping.get('brand')
        if brand_col and pd.notna(row.get(brand_col)):
            data['brand'] = str(row[brand_col]).strip()
        
        # Category
        data['category'] = sheet_name
        
        # Stock
        stock_col = mapping.get('stock')
        if stock_col:
            try:
                data['stock'] = int(float(row[stock_col])) if pd.notna(row[stock_col]) else 0
            except (ValueError, TypeError):
                data['stock'] = 0
        
        # Qty Sold
        qty_col = mapping.get('qty_sold')
        if qty_col:
            try:
                data['qty_sold'] = int(float(row[qty_col])) if pd.notna(row[qty_col]) else 0
            except (ValueError, TypeError):
                data['qty_sold'] = 0
        
        # Prices - handle X/Y format
        price_cols = {}
        for price_type in ['cost_price', 'price_normal', 'price_workshop']:
            col = mapping.get(price_type)
            if col:
                price_cols[price_type] = col
        
        # Parse prices
        for price_type, col in price_cols.items():
            if col and pd.notna(row.get(col)):
                val = str(row[col]).strip()
                # Handle X/Y format: use first value for workshop, second for normal
                if '/' in val:
                    parts = val.split('/')
                    try:
                        prices = []
                        for part in parts:
                            cleaned = ''.join(c for c in part if c.isdigit() or c == '.')
                            if cleaned:
                                prices.append(float(cleaned))
                        
                        if price_type == 'price_workshop' and len(prices) > 0:
                            data['price_workshop'] = prices[0]
                        elif price_type == 'price_normal' and len(prices) > 1:
                            data['price_normal'] = prices[1]
                        elif price_type == 'cost_price' and len(prices) > 0:
                            data['cost_price'] = prices[0]
                    except ValueError:
                        pass
                else:
                    # Single value
                    try:
                        cleaned = ''.join(c for c in val if c.isdigit() or c == '.')
                        if cleaned:
                            data[price_type] = float(cleaned)
                    except ValueError:
                        pass
        
        # Set defaults if prices not parsed
        if 'price_workshop' not in data:
            data['price_workshop'] = data.get('price_normal', 0)
        if 'price_normal' not in data:
            data['price_normal'] = data.get('price_workshop', 0)
        if 'cost_price' not in data:
            data['cost_price'] = data.get('price_workshop', 0)
        
        # Reorder level
        data['reorder_level'] = 10
        
        return data
    
    def _get_or_create_category(self, name: str) -> int:
        """
        Get or create category
        """
        from src.models.database import db
        
        result = db.execute_query(
            "SELECT category_id FROM categories WHERE LOWER(category_name) = LOWER(?)",
            (name,)
        )
        if result:
            return result[0]['category_id']
        
        return db.execute_insert(
            "INSERT INTO categories (category_name, description) VALUES (?, ?)",
            (name, f"Auto-created from import")
        )
    
    def _get_or_create_brand(self, name: str) -> int:
        """
        Get or create brand
        """
        from src.models.database import db
        
        if not name:
            name = 'Generic'
        
        name = str(name).strip().upper()
        
        result = db.execute_query(
            "SELECT brand_id FROM brands WHERE LOWER(brand_name) = LOWER(?)",
            (name,)
        )
        if result:
            return result[0]['brand_id']
        
        return db.execute_insert(
            "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
            (name, "Auto-created from import")
        )


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python importer.py <excel_file> [--validate-only]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    validate_only = '--validate-only' in sys.argv
    
    importer = RobustDataImporter()
    result = importer.import_from_excel(file_path, validate_only=validate_only)
    
    if result.get('valid'):
        print("\n[OK] Import completed successfully!")
    else:
        print("\n[FAIL] Import failed validation")
        sys.exit(1)
