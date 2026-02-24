import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, timedelta
import csv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
import utils.simple_table_styles as table_styles

class ReportsView:
    def __init__(self, parent):
        self.parent = parent
        self.create_reports_interface()
        self.current_report_data = None
    
    def create_reports_interface(self):
        """Create the reports interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Reports & Analytics",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Export button
        export_btn = ctk.CTkButton(
            header_frame,
            text="📥 Export CSV",
            command=self.export_report,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        export_btn.pack(side="right", padx=10, pady=10)
        
        # Content area with sidebar and report display
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Sidebar for report selection
        self.create_sidebar(content_frame)
        
        # Report display area
        self.create_report_display(content_frame)
    
    def create_sidebar(self, parent):
        """Create sidebar with report options"""
        sidebar = ctk.CTkFrame(parent)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=5)
        
        # Report Categories
        categories_label = ctk.CTkLabel(
            sidebar, 
            text="📋 Report Categories", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        categories_label.pack(pady=10)
        
        # Sales Reports
        sales_frame = ctk.CTkFrame(sidebar)
        sales_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sales_frame, text="💰 Sales Reports", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        ctk.CTkButton(
            sales_frame, text="Daily Sales", width=180,
            command=lambda: self.generate_sales_report("daily")
        ).pack(pady=2)
        
        ctk.CTkButton(
            sales_frame, text="Monthly Sales", width=180,
            command=lambda: self.generate_sales_report("monthly")
        ).pack(pady=2)
        
        ctk.CTkButton(
            sales_frame, text="Sales by Customer", width=180,
            command=self.generate_customer_sales_report
        ).pack(pady=2)
        
        # Purchase Reports
        purchase_frame = ctk.CTkFrame(sidebar)
        purchase_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(purchase_frame, text="🛒 Purchase Reports", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        ctk.CTkButton(
            purchase_frame, text="Purchase Summary", width=180,
            command=self.generate_purchase_summary
        ).pack(pady=2)
        
        ctk.CTkButton(
            purchase_frame, text="Purchases by Supplier", width=180,
            command=self.generate_supplier_purchases_report
        ).pack(pady=2)
        
        # Inventory Reports
        inventory_frame = ctk.CTkFrame(sidebar)
        inventory_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(inventory_frame, text="📦 Inventory Reports", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        ctk.CTkButton(
            inventory_frame, text="Stock Levels", width=180,
            command=self.generate_stock_report
        ).pack(pady=2)
        
        ctk.CTkButton(
            inventory_frame, text="Low Stock Alert", width=180,
            command=self.generate_low_stock_report
        ).pack(pady=2)
        
        ctk.CTkButton(
            inventory_frame, text="Product Valuation", width=180,
            command=self.generate_inventory_valuation
        ).pack(pady=2)
        
        # Financial Reports
        financial_frame = ctk.CTkFrame(sidebar)
        financial_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(financial_frame, text="💹 Financial Reports", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        ctk.CTkButton(
            financial_frame, text="Profit/Loss Analysis", width=180,
            command=self.generate_profit_loss_report
        ).pack(pady=2)
        
        ctk.CTkButton(
            financial_frame, text="Top Selling Products", width=180,
            command=self.generate_top_products_report
        ).pack(pady=2)
    
    def create_report_display(self, parent):
        """Create report display area"""
        display_frame = ctk.CTkFrame(parent)
        display_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        
        # Report title
        self.report_title = ctk.CTkLabel(
            display_frame,
            text="Select a report from the sidebar",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.report_title.pack(pady=20)
        
        # Report table
        table_frame = ctk.CTkFrame(display_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for report data with enhanced styling
        self.report_tree = ttk.Treeview(table_frame, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_reports_style(self.report_tree)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.report_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars with padding
        self.report_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        v_scrollbar.pack(side="right", fill="y", pady=5)
        h_scrollbar.pack(side="bottom", fill="x", padx=5)
    
    def display_report(self, title, columns, data):
        """Display report data in the table"""
        self.report_title.configure(text=title)
        self.current_report_data = {'title': title, 'columns': columns, 'data': data}
        
        # Clear existing data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Configure columns with enhanced styling
        self.report_tree['columns'] = columns
        for col in columns:
            self.report_tree.heading(col, text=f"  {col}  ", anchor="center")
            # Determine column width based on content
            if "Total" in col or "Amount" in col or "Value" in col or "Price" in col:
                width = 140
            elif "Product" in col or "Customer" in col or "Supplier" in col:
                width = 200
            elif "Description" in col or "Address" in col:
                width = 250
            else:
                width = 120
            self.report_tree.column(col, width=width, anchor="center", minwidth=80)
        
        # Add data
        for row in data:
            self.report_tree.insert("", "end", values=row)
    
    def generate_sales_report(self, period):
        """Generate sales report for specified period"""
        try:
            if period == "daily":
                title = "Daily Sales Report"
                date_filter = "DATE(s.sale_date) = DATE('now')"
            elif period == "monthly":
                title = "Monthly Sales Report"
                date_filter = "DATE(s.sale_date) >= DATE('now', 'start of month')"
            else:
                title = "Sales Report"
                date_filter = "1=1"
            
            query = f"""
                SELECT 
                    s.invoice_number as "Invoice",
                    DATE(s.sale_date) as "Date",
                    COALESCE(c.name, 'Walk-in Customer') as "Customer",
                    s.subtotal as "Subtotal",
                    s.tax as "Tax",
                    s.total_amount as "Total",
                    s.payment_method as "Payment",
                    s.status as "Status"
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE {date_filter}
                ORDER BY s.sale_date DESC
            """
            
            data = db.execute_query(query)
            columns = ["Invoice", "Date", "Customer", "Subtotal", "Tax", "Total", "Payment", "Status"]
            
            # Format data for display
            formatted_data = []
            total_sales = 0
            for row in data:
                formatted_row = [
                    row['Invoice'],
                    row['Date'],
                    row['Customer'],
                    f"${row['Subtotal']:.2f}",
                    f"${row['Tax']:.2f}",
                    f"${row['Total']:.2f}",
                    row['Payment'].title(),
                    row['Status'].title()
                ]
                formatted_data.append(formatted_row)
                total_sales += row['Total']
            
            # Add summary row
            if formatted_data:
                formatted_data.append(["-" * 50] * 8)
                formatted_data.append(["TOTAL", "", "", "", "", f"${total_sales:.2f}", "", f"{len(data)} sales"])
            
            self.display_report(f"{title} (Total: ${total_sales:.2f})", columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating sales report: {e}")
            messagebox.showerror("Error", f"Failed to generate sales report: {e}")
    
    def generate_customer_sales_report(self):
        """Generate sales report by customer"""
        try:
            query = """
                SELECT 
                    COALESCE(c.name, 'Walk-in Customer') as customer_name,
                    c.type as customer_type,
                    COUNT(s.id) as order_count,
                    SUM(s.total_amount) as total_spent,
                    AVG(s.total_amount) as avg_order_value,
                    MAX(s.sale_date) as last_purchase
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                GROUP BY s.customer_id, c.name, c.type
                ORDER BY total_spent DESC
            """
            
            data = db.execute_query(query)
            columns = ["Customer", "Type", "Orders", "Total Spent", "Avg Order", "Last Purchase"]
            
            # Format data for display
            formatted_data = []
            for row in data:
                formatted_row = [
                    row['customer_name'],
                    row['customer_type'] or "Walk-in",
                    str(row['order_count']),
                    f"${row['total_spent']:.2f}",
                    f"${row['avg_order_value']:.2f}",
                    row['last_purchase'] or "N/A"
                ]
                formatted_data.append(formatted_row)
            
            self.display_report("Sales by Customer", columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating customer sales report: {e}")
            messagebox.showerror("Error", f"Failed to generate customer sales report: {e}")
    
    def generate_purchase_summary(self):
        """Generate purchase summary report"""
        try:
            query = """
                SELECT 
                    p.invoice_number as "PO Number",
                    DATE(p.purchase_date) as "Date",
                    s.name as "Supplier",
                    COUNT(pi.id) as "Items",
                    p.total_amount as "Total",
                    p.status as "Status"
                FROM purchases p
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN purchase_items pi ON p.id = pi.purchase_id
                GROUP BY p.id
                ORDER BY p.purchase_date DESC
                LIMIT 50
            """
            
            data = db.execute_query(query)
            columns = ["PO Number", "Date", "Supplier", "Items", "Total", "Status"]
            
            # Format data for display
            formatted_data = []
            total_purchases = 0
            for row in data:
                formatted_row = [
                    row['PO Number'],
                    row['Date'],
                    row['Supplier'] or "Unknown",
                    str(row['Items']),
                    f"${row['Total']:.2f}",
                    row['Status'].title()
                ]
                formatted_data.append(formatted_row)
                total_purchases += row['Total']
            
            self.display_report(f"Purchase Summary (Total: ${total_purchases:.2f})", columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating purchase summary: {e}")
            messagebox.showerror("Error", f"Failed to generate purchase summary: {e}")
    
    def generate_supplier_purchases_report(self):
        """Generate purchases report by supplier"""
        try:
            query = """
                SELECT 
                    s.name as supplier_name,
                    s.contact_person,
                    COUNT(p.id) as order_count,
                    SUM(p.total_amount) as total_purchased,
                    AVG(p.total_amount) as avg_order_value,
                    MAX(p.purchase_date) as last_purchase
                FROM suppliers s
                LEFT JOIN purchases p ON s.supplier_id = p.supplier_id
                WHERE s.is_active = 1
                GROUP BY s.supplier_id
                ORDER BY total_purchased DESC
            """
            
            data = db.execute_query(query)
            columns = ["Supplier", "Contact Person", "Orders", "Total Purchased", "Avg Order", "Last Purchase"]
            
            # Format data for display
            formatted_data = []
            for row in data:
                formatted_row = [
                    row['supplier_name'],
                    row['contact_person'] or "N/A",
                    str(row['order_count'] or 0),
                    f"${row['total_purchased'] or 0:.2f}",
                    f"${row['avg_order_value'] or 0:.2f}",
                    row['last_purchase'] or "Never"
                ]
                formatted_data.append(formatted_row)
            
            self.display_report("Purchases by Supplier", columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating supplier purchases report: {e}")
            messagebox.showerror("Error", f"Failed to generate supplier purchases report: {e}")
    
    def generate_stock_report(self):
        """Generate current stock levels report"""
        try:
            query = """
                SELECT 
                    p.sku as "SKU",
                    p.name as "Product",
                    c.category_name as "Category",
                    b.brand_name as "Brand",
                    p.stock as "Current Stock",
                    p.reorder_level as "Reorder Level",
                    p.cost_price as "Cost Price",
                    (p.stock * p.cost_price) as "Stock Value"
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN brands b ON p.brand_id = b.brand_id
                WHERE p.is_active = 1
                ORDER BY p.name
            """
            
            data = db.execute_query(query)
            columns = ["SKU", "Product", "Category", "Brand", "Stock", "Reorder Level", "Cost Price", "Stock Value"]
            
            # Format data for display
            formatted_data = []
            total_value = 0
            for row in data:
                stock_value = (row['Current Stock'] or 0) * (row['Cost Price'] or 0)
                formatted_row = [
                    row['SKU'],
                    row['Product'],
                    row['Category'] or "N/A",
                    row['Brand'] or "N/A",
                    str(row['Current Stock'] or 0),
                    str(row['Reorder Level'] or 0),
                    f"${row['Cost Price'] or 0:.2f}",
                    f"${stock_value:.2f}"
                ]
                formatted_data.append(formatted_row)
                total_value += stock_value
            
            self.display_report(f"Stock Levels Report (Total Value: ${total_value:.2f})", columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating stock report: {e}")
            messagebox.showerror("Error", f"Failed to generate stock report: {e}")
    
    def generate_low_stock_report(self):
        """Generate low stock alert report"""
        try:
            query = """
                SELECT 
                    p.sku as "SKU",
                    p.name as "Product",
                    p.stock as "Current Stock",
                    p.reorder_level as "Reorder Level",
                    (p.reorder_level - p.stock) as "Needed",
                    p.cost_price as "Cost Price"
                FROM products p
                WHERE p.is_active = 1 AND p.stock <= p.reorder_level
                ORDER BY (p.reorder_level - p.stock) DESC
            """
            
            data = db.execute_query(query)
            columns = ["SKU", "Product", "Current Stock", "Reorder Level", "Qty Needed", "Cost Price"]
            
            # Format data for display
            formatted_data = []
            for row in data:
                formatted_row = [
                    row['SKU'],
                    row['Product'],
                    str(row['Current Stock']),
                    str(row['Reorder Level']),
                    str(max(0, row['Needed'])),
                    f"${row['Cost Price']:.2f}"
                ]
                formatted_data.append(formatted_row)
            
            title = f"Low Stock Alert ({len(formatted_data)} products need restocking)"
            self.display_report(title, columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating low stock report: {e}")
            messagebox.showerror("Error", f"Failed to generate low stock report: {e}")
    
    def generate_inventory_valuation(self):
        """Generate inventory valuation report"""
        try:
            query = """
                SELECT 
                    c.category_name as "Category",
                    COUNT(p.product_id) as "Products",
                    SUM(p.stock) as "Total Units",
                    SUM(p.stock * p.cost_price) as "Cost Value",
                    SUM(p.stock * p.price_normal) as "Retail Value",
                    SUM(p.stock * (p.price_normal - p.cost_price)) as "Potential Profit"
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active = 1
                GROUP BY c.category_id, c.category_name
                ORDER BY "Cost Value" DESC
            """
            
            data = db.execute_query(query)
            columns = ["Category", "Products", "Total Units", "Cost Value", "Retail Value", "Potential Profit"]
            
            # Format data for display
            formatted_data = []
            total_cost = 0
            total_retail = 0
            total_profit = 0
            
            for row in data:
                cost_value = row['Cost Value'] or 0
                retail_value = row['Retail Value'] or 0
                profit = row['Potential Profit'] or 0
                
                formatted_row = [
                    row['Category'] or "Uncategorized",
                    str(row['Products'] or 0),
                    str(row['Total Units'] or 0),
                    f"${cost_value:.2f}",
                    f"${retail_value:.2f}",
                    f"${profit:.2f}"
                ]
                formatted_data.append(formatted_row)
                total_cost += cost_value
                total_retail += retail_value
                total_profit += profit
            
            # Add totals
            if formatted_data:
                formatted_data.append(["-" * 20] * 6)
                formatted_data.append([
                    "TOTAL", "", "", 
                    f"${total_cost:.2f}", 
                    f"${total_retail:.2f}", 
                    f"${total_profit:.2f}"
                ])
            
            title = f"Inventory Valuation (Cost: ${total_cost:.2f}, Retail: ${total_retail:.2f})"
            self.display_report(title, columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating inventory valuation: {e}")
            messagebox.showerror("Error", f"Failed to generate inventory valuation: {e}")
    
    def generate_profit_loss_report(self):
        """Generate profit/loss analysis"""
        try:
            query = """
                SELECT 
                    'Sales Revenue' as item,
                    SUM(s.total_amount) as amount
                FROM sales s
                WHERE DATE(s.sale_date) >= DATE('now', 'start of month')
                UNION ALL
                SELECT 
                    'Purchase Costs' as item,
                    -SUM(p.total_amount) as amount
                FROM purchases p
                WHERE DATE(p.purchase_date) >= DATE('now', 'start of month')
            """
            
            data = db.execute_query(query)
            columns = ["Item", "Amount", "Percentage"]
            
            # Calculate totals
            revenue = 0
            costs = 0
            
            for row in data:
                if row['item'] == 'Sales Revenue':
                    revenue = row['amount'] or 0
                elif row['item'] == 'Purchase Costs':
                    costs = abs(row['amount'] or 0)
            
            profit = revenue - costs
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            # Format data for display
            formatted_data = [
                ["Sales Revenue", f"${revenue:.2f}", "100.0%"],
                ["Purchase Costs", f"${costs:.2f}", f"{(costs/revenue*100) if revenue > 0 else 0:.1f}%"],
                ["-" * 20, "-" * 20, "-" * 20],
                ["Net Profit/Loss", f"${profit:.2f}", f"{margin:.1f}%"]
            ]
            
            title = f"Profit/Loss Analysis (This Month) - Margin: {margin:.1f}%"
            self.display_report(title, columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating profit/loss report: {e}")
            messagebox.showerror("Error", f"Failed to generate profit/loss report: {e}")
    
    def generate_top_products_report(self):
        """Generate top selling products report"""
        try:
            query = """
                SELECT 
                    p.name as "Product",
                    p.sku as "SKU",
                    SUM(si.quantity) as "Qty Sold",
                    SUM(si.total) as "Revenue",
                    AVG(si.unit_price) as "Avg Price",
                    COUNT(DISTINCT s.id) as "Orders"
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.sale_date) >= DATE('now', '-30 days')
                GROUP BY p.product_id, p.name, p.sku
                ORDER BY "Qty Sold" DESC
                LIMIT 20
            """
            
            data = db.execute_query(query)
            columns = ["Product", "SKU", "Qty Sold", "Revenue", "Avg Price", "Orders"]
            
            # Format data for display
            formatted_data = []
            for row in data:
                formatted_row = [
                    row['Product'],
                    row['SKU'],
                    str(row['Qty Sold']),
                    f"${row['Revenue']:.2f}",
                    f"${row['Avg Price']:.2f}",
                    str(row['Orders'])
                ]
                formatted_data.append(formatted_row)
            
            title = "Top Selling Products (Last 30 days)"
            self.display_report(title, columns, formatted_data)
            
        except Exception as e:
            print(f"Error generating top products report: {e}")
            messagebox.showerror("Error", f"Failed to generate top products report: {e}")
    
    def export_report(self):
        """Export current report to CSV"""
        if not self.current_report_data:
            messagebox.showwarning("Warning", "Please generate a report first.")
            return
        
        # Ask user for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Report"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([f"Report: {self.current_report_data['title']}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([])  # Empty row
                    
                    # Write column headers
                    writer.writerow(self.current_report_data['columns'])
                    
                    # Write data
                    writer.writerows(self.current_report_data['data'])
                
                messagebox.showinfo("Success", f"Report exported successfully to {filename}")
                
            except Exception as e:
                print(f"Error exporting report: {e}")
                messagebox.showerror("Error", f"Failed to export report: {e}")
