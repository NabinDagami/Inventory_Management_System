"""

Excel Column Mapper - Automatic mapping with preview

"""



import pandas as pd

import sys

import os

from tkinter import filedialog, messagebox, ttk



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from models.database import db

from utils.sku_generator import SKUGenerator

import customtkinter as ctk

import tkinter as tk





class ExcelColumnMapper:

    """

    Excel import workflow:

    1. Show Excel raw data

    2. Show extracted/cleaned data

    3. Auto-map columns based on COLUMN_SUGGESTIONS

    4. Preview mapped data

    5. Import all data

    """



    DB_FIELDS = {

        'name': {'label': 'Product Name *', 'required': True, 'type': 'text'},

        'sku': {'label': 'SKU', 'required': False, 'type': 'text'},

        'category': {'label': 'Category', 'required': False, 'type': 'text'},

        'brand': {'label': 'Brand', 'required': False, 'type': 'text'},

        'description': {'label': 'Description', 'required': False, 'type': 'text'},

        'stock': {'label': 'Qty in Hand', 'required': False, 'type': 'number', 'default': 0},

        'qty_sold': {'label': 'Qty Sold', 'required': False, 'type': 'number', 'default': 0},

        'cost_price': {'label': 'Cost Price *', 'required': True, 'type': 'number'},

        'price_normal': {'label': 'Normal Price *', 'required': True, 'type': 'number'},

        'price_workshop': {'label': 'Workshop Price *', 'required': True, 'type': 'number'},

        'reorder_level': {'label': 'Reorder Level', 'required': False, 'type': 'number', 'default': 10}

    }



    COLUMN_SUGGESTIONS = {
        'name': ['Bike Names', 'bike names', 'Bikes names', 'Bikes Names', 'Bikes Tyre Sizes',
                 'Scooter Name', 'scooter name', 'Tyre', 'Helmet Name', 'helmet name',
                 'Items', 'items', 'Company names', 'Product Name', 'product name', 'Name', 'name'],
        'sku': ['SKU', 'sku', 'Code', 'code', 'Product Code'],
        'category': ['Category', 'category', 'Type', 'type'],
        'brand': ['Company', 'company', 'Brand', 'brand', 'Manufacturer'],
        'stock': ['Qty in Hand', 'Qty in hand', 'qty in hand', 'Qty in Hand/PCS', 'Stock', 'stock', 'Qty', 'Quantity'],
        'qty_sold': ['Qty Sold', 'Qty sold', 'qty sold', 'Qty Sold/PCS', 'Qty Sold/PCs', 'Sold', 'sold', 'Quantity Sold'],
        'cost_price': ['Cost', 'cost', 'Cost Price', 'cost price', 'Purchase Price', 'purchase price',
                       'Wholesale Price/PCS', 'Wholesale Price', 'Wholesale Price/set'],
        'price_normal': ['Retail Price', 'Retail price', 'retail price', 'Retail Price/PCS', 'Retail Price /PCS', 'Retail Price /set',
                         'Price', 'price', 'Normal Price', 'Selling Price', 'Last Price'],
        'price_workshop': ['Wholesale Price', 'Wholesale price', 'wholesale price', 'Wholesale Price/PCS', 'Wholesale Price/set',
                          'W/S Price', 'W/S', 'Workshop Price', 'workshop price', 'Workshop', 'Dealer Price'],
        'reorder_level': ['Reorder Level', 'Reorder', 'Reorder Point', 'Min Stock', 'Status']
    }



    EXCLUDE_SHEETS = ['Home', 'Home ', 'Dashboard', 'Sheet1', 'Daya form', '/']



    def __init__(self, parent_window):

        self.parent = parent_window

        self.file_path = None

        self.excel_file = None

        self.raw_sheets_data = []

        self.extracted_sheets_data = []

        self.excel_columns = []

        self.mappings = {}



    def browse_and_import(self):

        """Main workflow - Automatic mapping, no manual step needed"""

        # Step 1: Browse for file

        self.file_path = filedialog.askopenfilename(

            parent=self.parent,

            title="Select Excel File",

            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]

        )



        if not self.file_path:

            return



        # Show loading dialog while reading Excel

        if not self._show_loading_and_read_excel():

            return



        # Step 2: Show RAW Excel data

        if not self._show_raw_excel_data():

            return



        # Step 3: Extract data (with loading)

        if not self._extract_all_data_with_loading():

            return



        # Step 4: Show EXTRACTED data

        if not self._show_extracted_data():

            return



        # Step 5: AUTO-APPLY mappings (no manual dialog)

        self._auto_apply_mappings()



        if not self.mappings:

            messagebox.showerror("Error", "Could not automatically map columns. Please check your Excel file has the expected column names.")

            return



        # Step 6: Preview mapped data

        preview_data = self._get_mapped_preview()

        if not preview_data:

            messagebox.showerror("Error", "No data could be mapped. Please check your Excel file.")

            return



        if not self._show_mapped_preview(preview_data):

            return



        # Step 7: Import

        self._import_all_data()



    def _auto_apply_mappings(self):

        """Automatically apply column mappings based on COLUMN_SUGGESTIONS"""

        self.mappings = {}

        for field_key in self.DB_FIELDS.keys():

            suggested = self._suggest_mapping(field_key)

            if suggested:

                self.mappings[field_key] = suggested



    def _show_loading_and_read_excel(self):

        """Show loading dialog while reading Excel file"""

        loading = ctk.CTkToplevel(self.parent)

        loading.title("Reading Excel File...")

        loading.geometry("400x200")

        loading.transient(self.parent)

        loading.grab_set()

        loading.resizable(False, False)



        # Center

        loading.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 100

        loading.geometry(f"400x200+{x}+{y}")



        ctk.CTkLabel(loading, text="📂 Reading Excel File...",

                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)



        status = ctk.CTkLabel(loading, text=f"File: {os.path.basename(self.file_path)}")

        status.pack(pady=10)



        # Progress bar

        progress = ctk.CTkProgressBar(loading, width=300)

        progress.pack(pady=20)

        progress.set(0.3)

        loading.update()



        try:

            self.excel_file = pd.ExcelFile(self.file_path)

            progress.set(0.7)

            loading.update()



            # Small delay to show loading

            import time

            time.sleep(0.5)



            progress.set(1.0)

            loading.update()

            loading.destroy()

            return True



        except Exception as e:

            loading.destroy()

            messagebox.showerror("Error", f"Cannot open Excel file:\n{str(e)}")

            return False



    def _show_raw_excel_data(self):

        """Step 1: Show RAW Excel data - COMPACT SIZE"""

        dialog = ctk.CTkToplevel(self.parent)

        dialog.title("📊 Excel File - Raw Data View")

        dialog.geometry("1000x650")

        dialog.transient(self.parent)

        dialog.grab_set()



        # Center

        dialog.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 500

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 325

        dialog.geometry(f"1000x650+{x}+{y}")



        # Main container

        main_frame = ctk.CTkFrame(dialog)

        main_frame.pack(fill="both", expand=True, padx=10, pady=10)



        # Header

        header = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#3B82F6")

        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header, text="📊 Excel File - Raw Data View",

                    font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=8)



        # File info

        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(info_frame, text=f"File: {os.path.basename(self.file_path)}",

                    font=ctk.CTkFont(size=11)).pack(side="left")



        self.raw_sheets_data = []



        # Collect valid sheets first

        valid_sheets = []

        for sheet_name in self.excel_file.sheet_names:

            if sheet_name in self.EXCLUDE_SHEETS or sheet_name.startswith('/'):

                continue

            valid_sheets.append(sheet_name)



        if not valid_sheets:

            messagebox.showerror("Error", "No valid sheets found.")

            dialog.destroy()

            return False



        # Use dropdown for many sheets, tabs for few sheets

        if len(valid_sheets) > 10:

            # Dropdown selector for many sheets

            selector_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

            selector_frame.pack(fill="x", padx=10, pady=5)



            ctk.CTkLabel(selector_frame, text="📑 Select Sheet:",

                        font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))



            sheet_display_names = []

            for sheet_name in valid_sheets:

                try:

                    df_raw = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)

                    actual_rows = len(df_raw)

                    sheet_display_names.append(f"{sheet_name} ({actual_rows} rows)")

                except:

                    sheet_display_names.append(f"{sheet_name}")



            sheet_var = tk.StringVar(value=sheet_display_names[0])

            sheet_dropdown = ctk.CTkOptionMenu(selector_frame, values=sheet_display_names,

                                              variable=sheet_var, width=500, height=32,

                                              font=ctk.CTkFont(size=11))

            sheet_dropdown.pack(side="left", fill="x", expand=True)



            # Content frame - FIXED HEIGHT to ensure buttons visible

            content_frame = ctk.CTkFrame(main_frame)

            content_frame.pack(fill="both", expand=True, padx=10, pady=5)



            def show_raw_sheet_content(*args):

                # Clear previous content

                for widget in content_frame.winfo_children():

                    widget.destroy()



                selected_display = sheet_var.get()

                selected_sheet = selected_display.split(" (")[0]



                try:

                    df_raw = pd.read_excel(self.excel_file, sheet_name=selected_sheet, header=None, nrows=100)

                    actual_rows = len(pd.read_excel(self.excel_file, sheet_name=selected_sheet, header=None))



                    # Sheet info

                    ctk.CTkLabel(content_frame,

                                text=f"📄 Current Sheet: {selected_sheet} | {actual_rows} rows | {len(df_raw.columns)} cols",

                                font=ctk.CTkFont(size=13, weight="bold"), text_color="#3B82F6").pack(anchor="w", padx=5, pady=5)



                    # Treeview frame

                    tree_frame = ctk.CTkFrame(content_frame)

                    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)



                    max_cols = min(10, len(df_raw.columns))

                    columns = [f"Col {i+1}" for i in range(max_cols)]



                    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

                    tree.pack(side="left", fill="both", expand=True)



                    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)

                    v_scrollbar.pack(side="right", fill="y")

                    h_scrollbar = ttk.Scrollbar(content_frame, orient="horizontal", command=tree.xview)

                    h_scrollbar.pack(fill="x", padx=5)



                    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)



                    for i, col in enumerate(columns):

                        tree.heading(col, text=f"Column {i+1}")

                        tree.column(col, width=100, anchor="w")



                    for idx, row in df_raw.iterrows():

                        values = []

                        for i in range(max_cols):

                            val = row.iloc[i] if i < len(row) else ""

                            if pd.isna(val):

                                val = ""

                            else:

                                val = str(val)[:25]

                            values.append(val)

                        tree.insert("", "end", values=values)



                    if not any(s['sheet_name'] == selected_sheet for s in self.raw_sheets_data):

                        self.raw_sheets_data.append({

                            'sheet_name': selected_sheet,

                            'total_rows': actual_rows,

                            'total_cols': len(df_raw.columns)

                        })



                except Exception as e:

                    ctk.CTkLabel(content_frame, text=f"Error: {str(e)}",

                                font=ctk.CTkFont(size=11), text_color="red").pack(pady=30)



            sheet_var.trace('w', show_raw_sheet_content)

            show_raw_sheet_content()



        else:

            # Use tabs for fewer sheets

            tabview = ctk.CTkTabview(main_frame, width=950, height=480)

            tabview.pack(fill="both", expand=True, padx=10, pady=5)



            for sheet_name in valid_sheets:

                tab = tabview.add(sheet_name[:20])



                try:

                    df_raw = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None, nrows=100)

                    actual_rows = len(pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None))



                    ctk.CTkLabel(tab,

                                text=f"📄 Sheet: {sheet_name} | {actual_rows} rows | {len(df_raw.columns)} cols",

                                font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B82F6").pack(anchor="w", padx=5, pady=5)



                    tree_frame = ctk.CTkFrame(tab)

                    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)



                    max_cols = min(10, len(df_raw.columns))

                    columns = [f"Col {i+1}" for i in range(max_cols)]



                    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)

                    tree.pack(side="left", fill="both", expand=True)



                    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)

                    v_scrollbar.pack(side="right", fill="y")

                    h_scrollbar = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)

                    h_scrollbar.pack(fill="x", padx=5)



                    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)



                    for i, col in enumerate(columns):

                        tree.heading(col, text=f"Column {i+1}")

                        tree.column(col, width=100, anchor="w")



                    for idx, row in df_raw.iterrows():

                        values = []

                        for i in range(max_cols):

                            val = row.iloc[i] if i < len(row) else ""

                            if pd.isna(val):

                                val = ""

                            else:

                                val = str(val)[:25]

                            values.append(val)

                        tree.insert("", "end", values=values)



                    self.raw_sheets_data.append({

                        'sheet_name': sheet_name,

                        'total_rows': actual_rows,

                        'total_cols': len(df_raw.columns)

                    })



                except Exception as e:

                    ctk.CTkLabel(tab, text=f"Error: {str(e)}",

                                font=ctk.CTkFont(size=11), text_color="red").pack(pady=30)



        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        btn_frame.pack(side="bottom", fill="x", padx=10, pady=(5, 10))



        total_rows = sum(s['total_rows'] for s in self.raw_sheets_data) if self.raw_sheets_data else 0

        ctk.CTkLabel(btn_frame, text=f"Total: {len(self.raw_sheets_data)} sheets, {total_rows} rows",

                    font=ctk.CTkFont(size=11)).pack(side="left")



        result = {"proceed": False}



        def on_continue():

            result["proceed"] = True

            dialog.destroy()



        ctk.CTkButton(btn_frame, text="Extract Data →", command=on_continue,

                     fg_color="#10B981", width=140, height=35,

                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")



        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,

                     fg_color="#6B7280", width=90, height=35).pack(side="right", padx=10)



        self.parent.wait_window(dialog)

        return result["proceed"]



    def _extract_all_data_with_loading(self):

        """Extract data with loading dialog"""

        loading = ctk.CTkToplevel(self.parent)

        loading.title("Extracting Data...")

        loading.geometry("400x200")

        loading.transient(self.parent)

        loading.grab_set()

        loading.resizable(False, False)



        loading.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 100

        loading.geometry(f"400x200+{x}+{y}")



        ctk.CTkLabel(loading, text="🔍 Extracting & Cleaning Data...",

                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)



        status = ctk.CTkLabel(loading, text="Processing sheets...")

        status.pack(pady=10)



        progress = ctk.CTkProgressBar(loading, width=300)

        progress.pack(pady=15)

        progress.set(0)

        loading.update()



        self.extracted_sheets_data = []

        total_sheets = len([s for s in self.excel_file.sheet_names

                           if s not in self.EXCLUDE_SHEETS and not s.startswith('/')])



        try:

            for idx, sheet_name in enumerate(self.excel_file.sheet_names):

                if sheet_name in self.EXCLUDE_SHEETS or sheet_name.startswith('/'):

                    continue



                progress.set((idx + 1) / total_sheets * 0.8)

                status.configure(text=f"Processing: {sheet_name}...")

                loading.update()



                try:
                    df_raw = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                    if len(df_raw) < 2:
                        continue

                    header_row = self._find_header_row(df_raw)
                    if header_row is None:
                        header_row = 0

                    # Extract column names from the header row (instead of re-reading Excel)
                    columns = []
                    for col_idx in range(len(df_raw.columns)):
                        col_value = df_raw.iloc[header_row, col_idx]
                        if pd.isna(col_value):
                            col_name = f"Column {col_idx + 1}"
                        else:
                            # Normalize header to improve auto-mapping robustness
                            # (e.g., "Whole sale price " -> "whole sale price")
                            raw = str(col_value)
                            col_name = " ".join(raw.split()).strip()
                        columns.append(col_name)

                    # Extract data rows after the header row
                    rows = []
                    # Get header values for duplicate check
                    header_values = [str(x).strip().lower() if pd.notna(x) else '' for x in df_raw.iloc[header_row]]
                    
                    for row_idx in range(header_row + 1, len(df_raw)):
                        row_dict = {}
                        for col_idx in range(len(df_raw.columns)):
                            col_name = columns[col_idx]
                            cell_value = df_raw.iloc[row_idx, col_idx]
                            row_dict[col_name] = None if pd.isna(cell_value) else cell_value
                        
                        # Skip empty rows
                        non_none_values = [str(v).strip() for v in row_dict.values() if v is not None and str(v).strip() != '']
                        if len(non_none_values) == 0:
                            continue
                            
                        # Skip duplicate header rows
                        row_values = [str(x).strip().lower() if pd.notna(x) else '' for x in df_raw.iloc[row_idx]]
                        if row_values == header_values:
                            continue
                            
                        rows.append(row_dict)



                    self.extracted_sheets_data.append({

                        'sheet_name': sheet_name,

                        'columns': columns,

                        'rows': rows,

                        'total_rows': len(rows),

                        'header_row': header_row

                    })



                except Exception as e:

                    print(f"Error processing sheet {sheet_name}: {e}")

                    continue



            if not self.extracted_sheets_data:

                loading.destroy()

                messagebox.showerror("Error", "No valid data found.")

                return False



            all_columns = set()

            for sheet_data in self.extracted_sheets_data:

                all_columns.update(sheet_data['columns'])

            self.excel_columns = sorted(list(all_columns))



            progress.set(1.0)

            loading.update()

            import time

            time.sleep(0.3)

            loading.destroy()

            return True



        except Exception as e:

            loading.destroy()

            messagebox.showerror("Error", f"Extraction failed:\n{str(e)}")

            return False



    def _find_header_row(self, df):
        """Find header row in dataframe"""
        # First, skip rows that are just single-word sheet titles
        for idx in range(min(10, len(df))):
            row = df.iloc[idx]
            non_nan_values = [str(x).strip() for x in row if pd.notna(x) and str(x).strip() != '']
            
            if len(non_nan_values) == 1:
                # Skip single-word/single-value rows (they're usually sheet titles)
                continue
                
            row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
            if any(k in row_str for k in ['company', 'bike', 'price', 'qty', 'stock', 'names', 'scooter', 'helmet']):
                return idx
        
        # If no header found by keywords, try first row with multiple values
        for idx in range(min(10, len(df))):
            row = df.iloc[idx]
            non_nan_values = [str(x).strip() for x in row if pd.notna(x) and str(x).strip() != '']
            if len(non_nan_values) >= 2:
                return idx
                
        return 0



    def _to_float(self, value, default=0.0):

        try:

            if value is None:

                return float(default)

            s = str(value).strip().replace(',', '')

            if s == '':

                return float(default)

            # Handle X/Y price format - parse first value

            if '/' in s:

                parts = s.split('/')

                if parts and parts[0]:

                    cleaned = ''.join(c for c in parts[0] if c.isdigit() or c == '.')

                    if cleaned:

                        return float(cleaned)

            # Try to parse as plain number

            cleaned = ''.join(c for c in s if c.isdigit() or c == '.')

            if cleaned:

                return float(cleaned)

            return float(default)

        except Exception:

            return float(default)

    

    def _to_float_with_format(self, value, default=0.0):

        """

        Parse price value with format awareness:

        - 'X/Y' format: Returns X as workshop_price, should call separate method for Y as normal_price

        - Plain number: Returns as-is

        """

        price = self._to_float(value, default)

        if price == default and value and '/' in str(value):

            parts = str(value).split('/')

            try:

                first = ''.join(c for c in parts[0] if c.isdigit() or c == '.')

                second = ''.join(c for c in parts[1] if c.isdigit() or c == '.') if len(parts) > 1 else first

                return float(first) if first else default, float(second) if second else default

            except:

                return price, price

        return price, price



    def _to_int(self, value, default=0):

        try:

            return int(self._to_float(value, default))

        except Exception:

            return int(default)



    def _show_extracted_data(self):

        """Step 2: Show EXTRACTED data - COMPACT SIZE"""

        dialog = ctk.CTkToplevel(self.parent)

        dialog.title("📋 Extracted Data View")

        dialog.geometry("1000x650")

        dialog.transient(self.parent)

        dialog.grab_set()



        dialog.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 500

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 325

        dialog.geometry(f"1000x650+{x}+{y}")



        main_frame = ctk.CTkFrame(dialog)

        main_frame.pack(fill="both", expand=True, padx=10, pady=10)



        header = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#10B981")

        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header, text="📋 Extracted & Cleaned Data",

                    font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=8)



        total_rows = sum(s['total_rows'] for s in self.extracted_sheets_data)

        ctk.CTkLabel(main_frame,

                    text=f"Found {len(self.extracted_sheets_data)} sheets with {total_rows} total rows.",

                    font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=5)



        # Create tabs - COMPACT

        tabview = ctk.CTkTabview(main_frame, width=950, height=480)

        tabview.pack(fill="both", expand=True, padx=10, pady=5)



        for sheet_data in self.extracted_sheets_data:

            tab = tabview.add(sheet_data['sheet_name'][:20])



            ctk.CTkLabel(tab,

                        text=f"Sheet: {sheet_data['sheet_name']} | Row {sheet_data['header_row'] + 1} | {sheet_data['total_rows']} rows",

                        font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=5, pady=3)



            tree_frame = ctk.CTkFrame(tab)

            tree_frame.pack(fill="both", expand=True, padx=5, pady=5)



            display_cols = sheet_data['columns'][:8]

            tree = ttk.Treeview(tree_frame, columns=display_cols, show="headings", height=18)

            tree.pack(side="left", fill="both", expand=True)



            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)

            v_scrollbar.pack(side="right", fill="y")

            h_scrollbar = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)

            h_scrollbar.pack(fill="x", padx=5)



            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)



            for col in display_cols:

                tree.heading(col, text=col[:20])

                tree.column(col, width=110, anchor="w")



            for row in sheet_data['rows'][:50]:

                values = [str(row.get(col, ''))[:25] for col in display_cols]

                tree.insert("", "end", values=values)



            if len(sheet_data['rows']) > 50:

                ctk.CTkLabel(tab, text=f"... {len(sheet_data['rows']) - 50} more rows",

                            font=ctk.CTkFont(size=9), text_color="gray").pack(anchor="w", padx=5)



        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        btn_frame.pack(side="bottom", fill="x", padx=10, pady=(5, 10))



        result = {"proceed": False, "back": False}



        def on_continue():

            result["proceed"] = True

            dialog.destroy()



        def on_back():

            result["back"] = True

            dialog.destroy()



        ctk.CTkButton(btn_frame, text="Preview & Import →", command=on_continue,

                     fg_color="#3B82F6", width=150, height=35,

                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")



        ctk.CTkButton(btn_frame, text="← Back", command=on_back,

                     fg_color="#6B7280", width=100, height=35).pack(side="left")



        self.parent.wait_window(dialog)



        if result.get("back"):

            return self._show_raw_excel_data()



        return result.get("proceed", False)



    def _suggest_mapping(self, field_key):

        """Suggest Excel column for a database field"""

        suggestions = self.COLUMN_SUGGESTIONS.get(field_key, [])

        for col in self.excel_columns:

            if col in suggestions:

                return col

        return None



    def _get_mapped_preview(self):

        """Get preview of mapped data"""

        preview = []



        for sheet_data in self.extracted_sheets_data:

            for row in sheet_data['rows'][:10]:

                product = {'sheet': sheet_data['sheet_name']}

                for db_field, excel_col in self.mappings.items():

                    val = row.get(excel_col)

                    product[db_field] = None if pd.isna(val) else val



                if product.get('name'):

                    preview.append(product)



        return preview[:20]



    def _show_mapped_preview(self, preview_data):

        """Show preview of mapped data - COMPACT SIZE"""

        dialog = ctk.CTkToplevel(self.parent)

        dialog.title("👁️ Preview Extracted Data")

        dialog.geometry("900x650")

        dialog.transient(self.parent)

        dialog.grab_set()

        dialog.resizable(False, False)



        # Center the dialog

        dialog.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 450

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 325

        dialog.geometry(f"900x650+{x}+{y}")



        # Main container with fixed layout

        main_frame = ctk.CTkFrame(dialog)

        main_frame.pack(fill="both", expand=True, padx=10, pady=10)



        # Header

        header = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#F59E0B")

        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header, text="👁️ Preview Extracted Data",

                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=10)



        # Summary

        total_rows = sum(s['total_rows'] for s in self.extracted_sheets_data)

        ctk.CTkLabel(main_frame, text=f"Total products to import: {total_rows}",

                    font=ctk.CTkFont(size=13, weight="bold")).pack(pady=5)



        # Mappings display - fixed height

        map_frame = ctk.CTkFrame(main_frame, fg_color="#374151")

        map_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(map_frame, text="✓ Auto-detected Mappings:",

                    font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=3)



        for db_field, excel_col in self.mappings.items():

            label = self.DB_FIELDS[db_field]['label'].replace('*', '').strip()

            ctk.CTkLabel(map_frame, text=f"  • {label} → '{excel_col}'",

                        font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)



        # Treeview area - use pack instead of grid for consistency

        tree_frame = ctk.CTkFrame(main_frame)

        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)



        columns = ["Sheet", "Name"]

        if 'brand' in self.mappings:

            columns.append("Brand")

        if 'stock' in self.mappings:

            columns.append("Qty in Hand")

        if 'qty_sold' in self.mappings:

            columns.append("Qty Sold")

        if 'stock' in self.mappings and 'qty_sold' in self.mappings:

            columns.append("Available")

        if 'cost_price' in self.mappings:

            columns.append("Cost")

        if 'price_normal' in self.mappings:

            columns.append("Price")



        # Create treeview with pack layout

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        tree.pack(side="left", fill="both", expand=True)



        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)

        v_scrollbar.pack(side="right", fill="y")

        tree.configure(yscrollcommand=v_scrollbar.set)



        # Horizontal scrollbar in separate frame below tree

        h_scroll_frame = ctk.CTkFrame(main_frame, height=20)

        h_scroll_frame.pack(fill="x", padx=10, pady=(0, 5))

        h_scroll_frame.pack_propagate(False)

        

        h_scrollbar = ttk.Scrollbar(h_scroll_frame, orient="horizontal", command=tree.xview)

        h_scrollbar.pack(fill="x", expand=True)

        tree.configure(xscrollcommand=h_scrollbar.set)



        def _on_mousewheel(event):

            delta = event.delta

            if delta == 0:

                return

            tree.yview_scroll(int(-1 * (delta / 120)), "units")

            return "break"



        def _on_linux_scroll_up(event):

            tree.yview_scroll(-1, "units")

            return "break"



        def _on_linux_scroll_down(event):

            tree.yview_scroll(1, "units")

            return "break"



        tree.bind("<MouseWheel>", _on_mousewheel)

        tree.bind("<Button-4>", _on_linux_scroll_up)

        tree.bind("<Button-5>", _on_linux_scroll_down)

        tree.bind("<Enter>", lambda e: tree.focus_set())



        for col in columns:

            tree.heading(col, text=col)

            tree.column(col, width=100 if col != "Name" else 220)



        for product in preview_data:

            values = [product.get('sheet', ''), str(product.get('name', ''))[:35]]

            if 'brand' in self.mappings:

                values.append(str(product.get('brand', '')))

            if 'stock' in self.mappings:

                values.append(str(product.get('stock', 0)))

            if 'qty_sold' in self.mappings:

                values.append(str(product.get('qty_sold', 0)))

            if 'stock' in self.mappings and 'qty_sold' in self.mappings:

                stock_val = product.get('stock', 0)

                qty_sold_val = product.get('qty_sold', 0)

                available = self._to_int(stock_val) - self._to_int(qty_sold_val)

                values.append(str(available))

            if 'cost_price' in self.mappings:

                cost = product.get('cost_price', 0)

                values.append(f"₹{cost}" if cost else "")

            if 'price_normal' in self.mappings:

                price = product.get('price_normal', 0)

                values.append(f"₹{price}" if price else "")



            tree.insert("", "end", values=values)



        # Buttons at the bottom - always visible

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        btn_frame.pack(fill="x", padx=10, pady=(5, 10))



        result = {"proceed": False}



        def on_import():

            result["proceed"] = True

            dialog.destroy()



        def on_cancel():

            dialog.destroy()



        ctk.CTkButton(btn_frame, text="← Back", command=on_cancel,

                     fg_color="#6B7280", width=100, height=35).pack(side="left")



        ctk.CTkButton(btn_frame, text="✓ Import All Data", command=on_import,

                     fg_color="#10B981", width=160, height=35,

                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")



        self.parent.wait_window(dialog)



        return result.get("proceed", False)



    def _import_all_data(self):

        """Import all data with loading dialog"""

        loading = ctk.CTkToplevel(self.parent)

        loading.title("Importing Data...")

        loading.geometry("450x320")

        loading.transient(self.parent)

        loading.grab_set()

        loading.resizable(False, False)



        loading.update_idletasks()

        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 225

        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 160

        loading.geometry(f"450x320+{x}+{y}")



        header = ctk.CTkFrame(loading, corner_radius=10, fg_color="#10B981")

        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(header, text="📥 Importing Data",

                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=10)



        status_label = ctk.CTkLabel(loading, text="Starting import...",

                                   font=ctk.CTkFont(size=12))

        status_label.pack(pady=8)



        progress_bar = ctk.CTkProgressBar(loading, width=380)

        progress_bar.pack(pady=8)

        progress_bar.set(0)



        progress_text = ctk.CTkTextbox(loading, height=100, font=ctk.CTkFont(size=10))

        progress_text.pack(fill="both", expand=True, padx=15, pady=5)

        progress_text.insert("1.0", "Initializing...\n")



        stats = {

            'imported': 0,

            'errors': [],

            'categories_created': 0,

            'brands_created': 0

        }



        total_products = sum(s['total_rows'] for s in self.extracted_sheets_data)



        def update_status(msg):

            progress_text.insert("end", f"{msg}\n")

            progress_text.see("end")

            loading.update_idletasks()



        try:

            imported_count = 0

            total_sheets = len(self.extracted_sheets_data)



            for sheet_idx, sheet_data in enumerate(self.extracted_sheets_data):

                status_label.configure(

                    text=f"Sheet {sheet_idx + 1}/{total_sheets}: {sheet_data['sheet_name']}"

                )

                update_status(f"Processing: {sheet_data['sheet_name']}")



                category_id = self._get_or_create_category(sheet_data['sheet_name'])

                if category_id:

                    stats['categories_created'] += 1



                for row_idx, row in enumerate(sheet_data['rows']):

                    try:

                        product_data = {}

                        for db_field, excel_col in self.mappings.items():

                            val = row.get(excel_col)

                            product_data[db_field] = None if pd.isna(val) else val


                        if not product_data.get('name'):

                            continue


                        brand_name = product_data.get('brand', 'Generic')

                        brand_id = self._get_or_create_brand(brand_name)


                        stock = self._to_int(product_data.get('stock', 0))

                        qty_sold = self._to_int(product_data.get('qty_sold', 0))

                        cost_price = self._to_float(product_data.get('cost_price', 0))

                        price_normal_val = self._to_float(product_data.get('price_normal', 0))

                        workshop_price_val = self._to_float(product_data.get('price_workshop', 0))

                        # Initialize all price variables first!
                        price_normal = price_normal_val
                        workshop_price = workshop_price_val if workshop_price_val > 0 else price_normal_val

                        # Check if any price columns contain X/Y format
                        ws_val = product_data.get('price_workshop')
                        normal_val = product_data.get('price_normal')
                        cost_val = product_data.get('cost_price')

                        # Parse X/Y formatted prices
                        if ws_val and '/' in str(ws_val):
                            parts = str(ws_val).split('/')
                            try:
                                first = float(''.join(c for c in parts[0] if c.isdigit() or c == '.') or 0)
                                second = float(''.join(c for c in parts[1] if c.isdigit() or c == '.') or 0) if len(parts) > 1 else first
                                workshop_price = first
                                price_normal = second
                            except:
                                pass
                        elif normal_val and '/' in str(normal_val):
                            parts = str(normal_val).split('/')
                            try:
                                first = float(''.join(c for c in parts[0] if c.isdigit() or c == '.') or 0)
                                second = float(''.join(c for c in parts[1] if c.isdigit() or c == '.') or 0) if len(parts) > 1 else first
                                workshop_price = first
                                price_normal = second
                            except:
                                pass
                        elif cost_val and '/' in str(cost_val):
                            parts = str(cost_val).split('/')
                            try:
                                first = float(''.join(c for c in parts[0] if c.isdigit() or c == '.') or 0)
                                second = float(''.join(c for c in parts[1] if c.isdigit() or c == '.') or 0) if len(parts) > 1 else first
                                workshop_price = first
                                price_normal = second
                            except:
                                pass

                        # If workshop was explicitly set, use it
                        if workshop_price_val > 0:
                            workshop_price = workshop_price_val

                        # If Excel doesn't have cost price, keep it as 0 (there is no cost data in the sheet)
                        # Otherwise, use the parsed cost_price value.
                        if cost_price is None:
                            cost_price = 0
                        # If parsed cost_price is 0/empty, leave it as 0.

                        reorder_level = self._to_int(product_data.get('reorder_level', max(stock + 5, 10) if stock < 5 else 10))

                        # Calculate available_stock
                        available_stock = stock - qty_sold

                        sku = SKUGenerator.generate_sku(category_id, brand_id)

                        db.execute_insert("""
                            INSERT INTO products (name, sku, category_id, brand_id, stock, qty_sold,
                                                price_normal, price_workshop, cost_price, reorder_level,
                                                available_stock, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                        """, (
                            product_data['name'], sku, category_id, brand_id, stock, qty_sold,
                            price_normal, workshop_price, cost_price, reorder_level,
                            available_stock
                        ))

                        imported_count += 1
                        stats['imported'] = imported_count
                        progress = imported_count / total_products
                        progress_bar.set(min(progress, 0.99))

                        if imported_count % 10 == 0:
                            status_label.configure(

                                text=f"Imported {imported_count} of {total_products} products..."

                            )

                            loading.update_idletasks()



                    except Exception as e:

                        stats['errors'].append(f"Row {row_idx + 1} in {sheet_data['sheet_name']}: {str(e)}")



                update_status(f"✓ Completed: {sheet_data['sheet_name']}")



            progress_bar.set(1.0)

            loading.update()

            loading.destroy()



            msg = f"✓ Import Complete!\n\n"

            msg += f"Products imported: {stats['imported']}\n"

            msg += f"Categories created: {stats['categories_created']}\n"

            msg += f"Brands created: {stats['brands_created']}\n"

            if stats['errors']:

                msg += f"\nErrors: {len(stats['errors'])}\n"

                for err in stats['errors'][:5]:

                    msg += f"  - {err}\n"



            messagebox.showinfo("Import Complete", msg)



        except Exception as e:

            loading.destroy()

            messagebox.showerror("Import Error", f"Import failed:\n{str(e)}")



    def _get_or_create_category(self, name):

        """Get or create category"""

        result = db.execute_query(

            "SELECT category_id FROM categories WHERE LOWER(category_name) = LOWER(?)",

            (name,)

        )

        if result:

            return result[0]['category_id']



        return db.execute_insert(

            "INSERT INTO categories (category_name, description) VALUES (?, ?)",

            (name, f"Imported from {name}")

        )



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



        return db.execute_insert(

            "INSERT INTO brands (brand_name, description) VALUES (?, ?)",

            (name, "Imported from Excel")

        )

