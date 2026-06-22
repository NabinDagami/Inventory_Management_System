import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from utils.format_utils import format_price_with_decimals

class Dashboard:
    def __init__(self, parent, navigation_callbacks=None):
        self.parent = parent
        self.navigation_callbacks = navigation_callbacks or {}
        self.create_dashboard()
        self.load_dashboard_data()
    
    def create_dashboard(self):
        """Create the dashboard layout"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product Search Section
        self.create_product_search_section(main_frame)
        
        # KPI Cards Row
        kpi_frame = ctk.CTkFrame(main_frame)
        kpi_frame.pack(fill="x", pady=(0, 20))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create KPI cards
        self.create_kpi_cards(kpi_frame)
        
        # Charts Row
        charts_frame = ctk.CTkFrame(main_frame)
        charts_frame.pack(fill="both", expand=True)
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Create charts
        self.create_charts(charts_frame)
        
        # Quick Actions and Recent Activity
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", pady=(20, 0))
        bottom_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.create_quick_actions(bottom_frame)
        self.create_recent_activity(bottom_frame)
    
    def create_kpi_cards(self, parent):
        """Create KPI cards for key metrics"""
        # Total Sales
        sales_card = self.create_kpi_card(
            parent, "💰 Total Sales", "0", "This Month", "green"
        )
        sales_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Total Products
        products_card = self.create_kpi_card(
            parent, "📦 Total Products", "0", "In Stock", "blue"
        )
        products_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Low Stock Items
        stock_card = self.create_kpi_card(
            parent, "⚠️ Low Stock", "0", "Items", "orange"
        )
        stock_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Total Customers
        customers_card = self.create_kpi_card(
            parent, "👥 Customers", "0", "Active", "purple"
        )
        customers_card.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Store references for updating
        self.kpi_cards = {
            'sales': sales_card,
            'products': products_card,
            'low_stock': stock_card,
            'customers': customers_card
        }
    
    def create_kpi_card(self, parent, title, value, subtitle, color):
        """Create a single KPI card"""
        card = ctk.CTkFrame(parent)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.get_color(color)
        )
        value_label.pack(pady=5)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Store labels for updating
        card.value_label = value_label
        card.subtitle_label = subtitle_label
        
        return card
    
    def get_color(self, color_name):
        """Get color based on theme"""
        colors = {
            'green': ("#10B981", "#10B981"),
            'blue': ("#3B82F6", "#3B82F6"),
            'orange': ("#F59E0B", "#F59E0B"),
            'purple': ("#8B5CF6", "#8B5CF6"),
            'red': ("#EF4444", "#EF4444")
        }
        return colors.get(color_name, ("#3B82F6", "#3B82F6"))
    
    def create_product_search_section(self, parent):
        """Create product search section with search bar and details display"""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Quick Product Search",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Search input frame
        input_frame = ctk.CTkFrame(search_frame)
        input_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Search by product name or SKU...",
            font=ctk.CTkFont(size=13),
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        # Search button
        search_btn = ctk.CTkButton(
            input_frame,
            text="🔍 Search",
            command=self.search_product,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            input_frame,
            text="❌ Clear",
            command=self.clear_search,
            width=80,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left", pady=10)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.search_product())
        
        # Product details frame (initially hidden)
        self.details_frame = ctk.CTkFrame(search_frame)
        
        # Create product details labels
        self.create_product_details_display()
    
    def create_product_details_display(self):
        """Create labels to display product details"""
        # Results count label
        self.results_count_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        self.results_count_label.pack(pady=(5, 0))
        
        # Create scrollable frame for product list
        self.results_list_frame = ctk.CTkScrollableFrame(self.details_frame, height=150)
        self.results_list_frame.pack(fill="x", padx=20, pady=10)
        
        # Selected product details header
        self.details_header = ctk.CTkLabel(
            self.details_frame,
            text="📦 Selected Product Details",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.details_header.pack(pady=(10, 5))
        
        # Details grid
        details_grid = ctk.CTkFrame(self.details_frame)
        details_grid.pack(fill="x", padx=20, pady=10)
        details_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 1
        self.sku_label = self.create_detail_item(details_grid, "SKU:", "", 0, 0)
        self.name_label = self.create_detail_item(details_grid, "Name:", "", 0, 1)
        self.category_label = self.create_detail_item(details_grid, "Category:", "", 0, 2)
        self.brand_label = self.create_detail_item(details_grid, "Brand:", "", 0, 3)
        
        # Row 2
        self.stock_label = self.create_detail_item(details_grid, "Stock:", "", 1, 0)
        self.reorder_label = self.create_detail_item(details_grid, "Reorder Level:", "", 1, 1)
        self.cost_label = self.create_detail_item(details_grid, "Cost Price:", "", 1, 2)
        self.normal_price_label = self.create_detail_item(details_grid, "Normal Price:", "", 1, 3)
        
        # Row 3
        self.workshop_price_label = self.create_detail_item(details_grid, "Workshop Price:", "", 2, 0)
        self.status_label = self.create_detail_item(details_grid, "Status:", "", 2, 1)
        
        # Store search results
        self.search_results = []
    
    def create_detail_item(self, parent, label_text, value_text, row, column):
        """Create a single detail item with label and value"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=column, padx=10, pady=5, sticky="w")
        
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray50", "gray50")
        )
        label.pack(side="left")
        
        value = ctk.CTkLabel(
            frame,
            text=value_text,
            font=ctk.CTkFont(size=11)
        )
        value.pack(side="left", padx=(5, 0))
        
        return value
    
    def search_product(self):
        """Search for products and display results list"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        try:
            # Clear previous results and reset selected product
            for widget in self.results_list_frame.winfo_children():
                widget.destroy()
            self.selected_product_sku = None
            self.product_buttons = {}
            
            # Search by name or SKU (no limit - show all matches)
            query = """
                SELECT p.*, c.category_name, b.brand_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN brands b ON p.brand_id = b.brand_id
                WHERE (p.name LIKE ? OR p.sku LIKE ?) AND p.is_active = 1
                ORDER BY p.name
            """
            search_pattern = f"%{search_term}%"
            results = db.execute_query(query, (search_pattern, search_pattern))
            
            if results:
                self.search_results = results
                self.results_count_label.configure(text=f"Found {len(results)} product(s) matching '{search_term}'")
                
                # Create clickable buttons for each product
                for idx, product in enumerate(results):
                    product_btn = ctk.CTkButton(
                        self.results_list_frame,
                        text=f"📦 {product['name']} (SKU: {product['sku']})",
                        anchor="w",
                        command=lambda p=product, sku=product['sku']: self.select_product_from_list(p, sku),
                        height=30,
                        font=ctk.CTkFont(size=11),
                        fg_color=("gray85", "gray30"),
                        hover_color=("gray75", "gray40")
                    )
                    product_btn.pack(fill="x", pady=2)
                    self.product_buttons[product['sku']] = product_btn
                
                # Show the first product details by default and highlight it
                first_product = results[0]
                self.select_product_from_list(first_product, first_product['sku'])
            else:
                self.results_count_label.configure(text=f"No products found matching '{search_term}'")
                messagebox.showinfo("Not Found", f"No product found matching '{search_term}'.")
                self.details_frame.pack_forget()
                
        except Exception as e:
            print(f"Error searching product: {e}")
            messagebox.showerror("Error", f"Failed to search product: {e}")
    
    def select_product_from_list(self, product, sku):
        """Display details of a product selected from the list and highlight it"""
        # Reset previous selection color
        if self.selected_product_sku and self.selected_product_sku in self.product_buttons:
            prev_btn = self.product_buttons[self.selected_product_sku]
            prev_btn.configure(fg_color=("gray85", "gray30"), text_color=("gray10", "gray90"))
        
        # Highlight the selected button
        if sku in self.product_buttons:
            selected_btn = self.product_buttons[sku]
            selected_btn.configure(fg_color=("#3B82F6", "#2563EB"), text_color="white")
            self.selected_product_sku = sku
        
        # Display product details
        self.display_product_details(product)
    
    def display_product_details(self, product):
        """Display product details in the details frame"""
        # Update all labels with product data (handle sqlite3.Row as dict)
        self.sku_label.configure(text=product['sku'] if product['sku'] else 'N/A')
        self.name_label.configure(text=product['name'] if product['name'] else 'N/A')
        self.category_label.configure(text=product['category_name'] if product['category_name'] else 'N/A')
        self.brand_label.configure(text=product['brand_name'] if product['brand_name'] else 'N/A')
        
        stock = product['stock'] if product['stock'] else 0
        reorder_level = product['reorder_level'] if product['reorder_level'] else 0
        
        # Color code stock status
        if stock <= reorder_level:
            stock_text = f"{stock} ⚠️ Low Stock"
            stock_color = "#EF4444"  # Red
        else:
            stock_text = str(stock)
            stock_color = "#10B981"  # Green
        
        self.stock_label.configure(text=stock_text, text_color=stock_color)
        self.reorder_label.configure(text=str(reorder_level))
        
        cost_price = product['cost_price'] if product['cost_price'] else 0
        normal_price = product['price_normal'] if product['price_normal'] else 0
        workshop_price = product['price_workshop'] if product['price_workshop'] else 0
        
        self.cost_label.configure(text=format_price_with_decimals(cost_price))
        self.normal_price_label.configure(text=format_price_with_decimals(normal_price))
        self.workshop_price_label.configure(text=format_price_with_decimals(workshop_price))
        
        # Status
        is_active = product['is_active'] if product['is_active'] is not None else 1
        if is_active:
            status_text = "✅ Active"
            status_color = "#10B981"
        else:
            status_text = "❌ Inactive"
            status_color = "#EF4444"
        
        self.status_label.configure(text=status_text, text_color=status_color)
        
        # Show the details frame
        self.details_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    def clear_search(self):
        """Clear search and hide details"""
        self.search_entry.delete(0, 'end')
        self.details_frame.pack_forget()
    
    def create_charts(self, parent):
        """Create charts for data visualization"""
        # Sales Chart
        sales_frame = ctk.CTkFrame(parent)
        sales_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        self._create_coming_soon(sales_frame, "📈 Sales Overview (Last 7 Days)")

        # Product Categories Chart
        categories_frame = ctk.CTkFrame(parent)
        categories_frame.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")

        self._create_coming_soon(categories_frame, "🏷️ Product Categories")

        # Monthly Trends Chart
        trends_frame = ctk.CTkFrame(parent)
        trends_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=(10, 0), sticky="nsew")

        self._create_coming_soon(trends_frame, "📊 Monthly Sales vs Purchases Trend")

    def _create_coming_soon(self, parent, title_text):
        """Placeholder for charts not yet implemented."""
        title = ctk.CTkLabel(
            parent,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)

        # Dashed-border style placeholder area
        placeholder = ctk.CTkFrame(parent, fg_color=("gray95", "gray17"),
                                   corner_radius=12)
        placeholder.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        inner = ctk.CTkFrame(placeholder, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner,
            text="📊",
            font=ctk.CTkFont(size=40)
        ).pack()

        ctk.CTkLabel(
            inner,
            text="Coming Soon",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray50", "gray60")
        ).pack(pady=(8, 2))
    
    def create_quick_actions(self, parent):
        """Create quick actions panel"""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        title = ctk.CTkLabel(
            actions_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=15)
        
        # Action buttons
        actions = [
            ("➕ Add Product", self.add_product),
            ("💰 New Sale", self.new_sale),
            ("🛒 New Purchase", self.new_purchase),
            ("👤 Add Customer", self.add_customer)
        ]
        
        for text, command in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def create_recent_activity(self, parent):
        """Create recent activity panel"""
        activity_frame = ctk.CTkFrame(parent)
        activity_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        title = ctk.CTkLabel(
            activity_frame,
            text="📋 Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=15)
        
        # Activity list (scrollable)
        activity_list = ctk.CTkScrollableFrame(activity_frame, height=200)
        activity_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sample activities
        activities = [
            (f"💰 Sale #001 - {format_price_with_decimals(250)}", "2 hours ago"),
            ("� Low stock alert: Product ABC", "3 hours ago"),
            ("🛒 Purchase #PO001 received", "5 hours ago"),
            ("�👤 New customer: John Doe", "1 day ago"),
            ("📊 Monthly report generated", "2 days ago")
        ]
        
        for activity, time in activities:
            activity_item = ctk.CTkFrame(activity_list)
            activity_item.pack(fill="x", pady=2)
            
            activity_label = ctk.CTkLabel(
                activity_item,
                text=activity,
                anchor="w",
                font=ctk.CTkFont(size=12)
            )
            activity_label.pack(side="left", padx=10, pady=5)
            
            time_label = ctk.CTkLabel(
                activity_item,
                text=time,
                anchor="e",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray50")
            )
            time_label.pack(side="right", padx=10, pady=5)
    
    def load_dashboard_data(self):
        """Load actual data from database and update KPIs"""
        try:
            # Get total sales this month
            current_month = datetime.now().strftime("%Y-%m")
            sales_query = f"""
                SELECT SUM(total_amount) as total_sales
                FROM sales 
                WHERE strftime('%Y-%m', sale_date) = ?
            """
            sales_result = db.execute_query(sales_query, (current_month,))
            total_sales = sales_result[0]['total_sales'] if sales_result[0]['total_sales'] else 0
            
            # Get total products
            products_query = "SELECT COUNT(*) as total_products FROM products WHERE is_active = 1"
            products_result = db.execute_query(products_query)
            total_products = products_result[0]['total_products']
            
            # Get low stock items
            low_stock_query = "SELECT COUNT(*) as low_stock FROM products WHERE stock <= reorder_level AND is_active = 1"
            low_stock_result = db.execute_query(low_stock_query)
            low_stock_count = low_stock_result[0]['low_stock']
            
            # Get active customers
            customers_query = "SELECT COUNT(*) as total_customers FROM customers WHERE is_active = 1"
            customers_result = db.execute_query(customers_query)
            total_customers = customers_result[0]['total_customers']
            
            # Update KPI cards
            self.kpi_cards['sales'].value_label.configure(text=format_price_with_decimals(total_sales))
            self.kpi_cards['products'].value_label.configure(text=str(total_products))
            self.kpi_cards['low_stock'].value_label.configure(text=str(low_stock_count))
            self.kpi_cards['customers'].value_label.configure(text=str(total_customers))
            
            # Update colors based on values
            if low_stock_count > 0:
                self.kpi_cards['low_stock'].value_label.configure(text_color=self.get_color('red'))
            else:
                self.kpi_cards['low_stock'].value_label.configure(text_color=self.get_color('green'))
                
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    # Quick action methods
    def add_product(self):
        """Quick action: Navigate to Inventory to add new product"""
        if 'inventory' in self.navigation_callbacks:
            self.navigation_callbacks['inventory']()
        else:
            messagebox.showinfo("Info", "Navigate to Inventory → Products to add new products.")
    
    def new_sale(self):
        """Quick action: Navigate to Sales to create new sale"""
        if 'sales' in self.navigation_callbacks:
            self.navigation_callbacks['sales']()
        else:
            messagebox.showinfo("Info", "Navigate to Sales module to create new sales.")
    
    def new_purchase(self):
        """Quick action: Navigate to Purchases to create new purchase"""
        if 'purchases' in self.navigation_callbacks:
            self.navigation_callbacks['purchases']()
        else:
            messagebox.showinfo("Info", "Navigate to Purchases module to create new purchase orders.")
    
    def add_customer(self):
        """Quick action: Navigate to Customers to add new customer"""
        if 'customers' in self.navigation_callbacks:
            self.navigation_callbacks['customers']()
        else:
            messagebox.showinfo("Info", "Navigate to Customers module to add new customers.")
