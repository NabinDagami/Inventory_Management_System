import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
import utils.simple_table_styles as table_styles

class SalesView:
    def __init__(self, parent):
        self.parent = parent
        self.cart_items = []
        self.current_customer = None
        self.discount_amount = 0
        self.discount_type = "amount"  # "amount" or "percentage"
        self.discount_percentage = 0
        self.create_sales_interface()
        self.load_customers()
        self.load_products()
    
    def create_sales_interface(self):
        """Create the sales management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame)
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.new_sale_btn = ctk.CTkButton(
            tab_frame,
            text="💰 New Sale",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("new_sale")
        )
        self.new_sale_btn.pack(side="left", padx=(0, 10))
        
        self.sales_history_btn = ctk.CTkButton(
            tab_frame,
            text="📋 Sales History",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("sales_history")
        )
        self.sales_history_btn.pack(side="left", padx=(0, 10))

        self.credit_payments_btn = ctk.CTkButton(
            tab_frame,
            text="💳 Credit Payments",
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("credit_payments")
        )
        self.credit_payments_btn.pack(side="left")

        # Current tab tracking
        self.current_tab = "new_sale"
        
        # Content container
        self.content_container = ctk.CTkFrame(main_frame)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=0)
        
        # Create all interfaces
        self.create_new_sale_interface()
        self.create_sales_history_interface()
        self.create_credit_payments_interface()

        # Show new sale interface by default
        self.switch_tab("new_sale")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab = tab_name

        # Update button styles
        active_color = ("#1f538d", "#14375e")
        inactive_color = ("gray85", "gray25")
        inactive_text_color = ("gray10", "gray90")
        
        if tab_name == "new_sale":
            self.new_sale_btn.configure(fg_color=active_color, text_color="white")
            self.sales_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_payments_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        elif tab_name == "sales_history":
            self.new_sale_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.sales_history_btn.configure(fg_color=active_color, text_color="white")
            self.credit_payments_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        else:  # credit_payments
            self.new_sale_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.sales_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_payments_btn.configure(fg_color=active_color, text_color="white")

        # Hide all frames first
        self.new_sale_frame.pack_forget()
        self.sales_history_frame.pack_forget()
        self.credit_payments_frame.pack_forget()

        # Show the selected tab
        if tab_name == "new_sale":
            self.new_sale_frame.pack(fill="both", expand=True)
        elif tab_name == "sales_history":
            self.sales_history_frame.pack(fill="both", expand=True)
            self.load_sales_history()
        elif tab_name == "credit_payments":
            self.credit_payments_frame.pack(fill="both", expand=True)
            self.load_credit_sales()
    
    def create_new_sale_interface(self):
        """Create the new sale interface"""
        self.new_sale_frame = ctk.CTkFrame(self.content_container)
        
        # Customer and payment selection header
        header_frame = ctk.CTkFrame(self.new_sale_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Customer selection
        customer_label = ctk.CTkLabel(header_frame, text="Customer:", font=ctk.CTkFont(size=14, weight="bold"))
        customer_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.customer_var = tk.StringVar(value="Walk-in Customer")
        self.customer_dropdown = ctk.CTkOptionMenu(
            header_frame, 
            variable=self.customer_var,
            command=self.on_customer_selected,
            width=200
        )
        self.customer_dropdown.pack(side="left", padx=5, pady=10)
        
        # Payment method
        payment_label = ctk.CTkLabel(header_frame, text="Payment:", font=ctk.CTkFont(size=14, weight="bold"))
        payment_label.pack(side="left", padx=(20, 5), pady=10)
        
        self.payment_var = tk.StringVar(value="Cash")
        payment_dropdown = ctk.CTkOptionMenu(
            header_frame,
            variable=self.payment_var,
            values=["Cash", "Credit"],
            width=100
        )
        payment_dropdown.pack(side="left", padx=5, pady=10)
        
        # Content area with two columns
        content_frame = ctk.CTkFrame(self.new_sale_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        content_frame.grid_columnconfigure(0, weight=4)  # Products section 
        content_frame.grid_columnconfigure(1, weight=6)  # Cart section gets more space
        content_frame.grid_rowconfigure(0, weight=1)     # Allow row to expand fully
        
        # Left side - Product selection
        self.create_product_selection(content_frame)
        
        # Right side - Cart and total
        self.create_cart_section(content_frame)
    
    def create_sales_history_interface(self):
        """Create the sales history interface"""
        self.sales_history_frame = ctk.CTkFrame(self.content_container)
        
        # Header with search and filters
        header_frame = ctk.CTkFrame(self.sales_history_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(header_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.sales_search_var = tk.StringVar()
        self.sales_search_var.trace('w', self.filter_sales_history)
        search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.sales_search_var,
            placeholder_text="Search by invoice number or customer...",
            width=300
        )
        search_entry.pack(side="left", padx=5, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_sales_history,
            width=100,
            height=35
        )
        refresh_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Sales history table - make fully scrollable
        table_frame = ctk.CTkFrame(self.sales_history_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=0)
        
        # Create scrollable frame for the table
        table_container = ctk.CTkScrollableFrame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        # Create treeview for sales history with enhanced styling
        columns = ("Invoice", "Date", "Customer", "Payment", "Items", "Discount", "Paid", "Credit", "Total", "Status")
        self.sales_history_tree = ttk.Treeview(table_container, columns=columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_sales_history_style(self.sales_history_tree)
        
        # Define headings and column widths - bigger columns
        column_widths = {"Invoice": 140, "Date": 110, "Customer": 180, "Payment": 90, 
                        "Items": 70, "Discount": 90, "Paid": 100, "Credit": 100, "Total": 110, "Status": 90}
        
        for col in columns:
            self.sales_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.sales_history_tree.column(col, width=column_widths.get(col, 120), anchor="center", minwidth=80)
        
        # Add both vertical and horizontal scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.sales_history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.sales_history_tree.xview)
        self.sales_history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars properly
        self.sales_history_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self.sales_history_frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        view_details_btn = ctk.CTkButton(
            actions_frame,
            text="👁️ View Details",
            command=self.view_sale_details,
            width=120,
            height=35
        )
        view_details_btn.pack(side="left", padx=5)

        pay_credit_btn = ctk.CTkButton(
            actions_frame,
            text="💰 Pay Credit",
            command=self.pay_credit_for_sale,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        pay_credit_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            actions_frame,
            text="🖨️ Export Invoice",
            command=self.export_invoice,
            width=130,
            height=35,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        export_btn.pack(side="left", padx=5)

        # Double-click to view details
        self.sales_history_tree.bind("<Double-1>", lambda e: self.view_sale_details())
    
    def load_sales_history(self):
        """Load sales history data"""
        try:
            query = """
                SELECT s.id as sale_id, s.invoice_number, s.sale_date, s.payment_method,
                       s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as credit,
                       s.discount, s.status, c.name as customer_name,
                       COUNT(si.id) as item_count
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                LEFT JOIN sale_items si ON s.id = si.sale_id
                GROUP BY s.id
                ORDER BY s.sale_date DESC, s.id DESC
            """
            sales = db.execute_query(query)
            
            # Clear existing items
            for item in self.sales_history_tree.get_children():
                self.sales_history_tree.delete(item)
            
            # Add sales to tree
            for sale in sales:
                customer_name = sale['customer_name'] or "Walk-in Customer"
                payment_method = sale['payment_method'].title()
                status = sale['status'].title()
                discount_amount = sale['discount'] or 0
                
                self.sales_history_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    payment_method,
                    sale['item_count'],
                    f"Rs{discount_amount:.2f}" if discount_amount > 0 else "-",
                    f"Rs{sale['paid_amount']:.2f}",
                    f"Rs{sale['total_amount'] - sale['paid_amount']:.2f}",
                    f"Rs{sale['total_amount']:.2f}",
                    status
                ))
            
            self.all_sales_data = sales
            
        except Exception as e:
            print(f"Error loading sales history: {e}")
            messagebox.showerror("Error", f"Failed to load sales history: {e}")
    
    def filter_sales_history(self, *args):
        """Filter sales history based on search"""
        search_term = self.sales_search_var.get().lower()
        
        # Clear tree
        for item in self.sales_history_tree.get_children():
            self.sales_history_tree.delete(item)
        
        if not hasattr(self, 'all_sales_data'):
            return
        
        # Filter and display matching sales
        for sale in self.all_sales_data:
            customer_name = sale['customer_name'] or "Walk-in Customer"
            
            if (search_term in sale['invoice_number'].lower() or
                search_term in customer_name.lower()):
                
                payment_method = sale['payment_method'].title()
                status = sale['status'].title()
                discount_amount = sale['discount'] or 0
                
                self.sales_history_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    payment_method,
                    sale['item_count'],
                    f"Rs{discount_amount:.2f}" if discount_amount > 0 else "-",
                    f"Rs{sale['paid_amount']:.2f}",
                    f"Rs{sale['total_amount'] - sale['paid_amount']:.2f}",
                    f"Rs{sale['total_amount']:.2f}",
                    status
                ))
    
    def view_sale_details(self):
        """View detailed information about a selected sale"""
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to view details.")
            return
        
        # Get selected sale data
        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]
        
        # Find sale in data
        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break
        
        if not selected_sale:
            messagebox.showerror("Error", "Sale details not found.")
            return
        
        # Create details dialog
        SaleDetailsDialog(self.parent, selected_sale)
    
    def create_product_selection(self, parent):
        """Create product selection area"""
        # Use regular frame instead of scrollable frame
        product_frame = ctk.CTkFrame(parent, corner_radius=6)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        
        # Configure frame to expand properly
        product_frame.grid_rowconfigure(2, weight=1)  # Make table area expand (row 2)
        product_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        title_label = ctk.CTkLabel(
            product_frame, 
            text="📦 Select Products", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))
        
        # Search box
        search_frame = ctk.CTkFrame(product_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 5))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(8, 5), pady=6)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        search_entry = ctk.CTkEntry(
            search_frame, 
            textvariable=self.search_var,
            placeholder_text="Product name or SKU..."
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 8), pady=6)
        
        # Products table container - this should expand to fill remaining space
        products_table_frame = ctk.CTkFrame(product_frame)
        products_table_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 5))
        products_table_frame.grid_rowconfigure(0, weight=1)
        products_table_frame.grid_columnconfigure(0, weight=1)
        
        # Create container for products table
        products_container = ctk.CTkFrame(products_table_frame)
        products_container.grid(row=0, column=0, sticky="nsew")
        products_container.grid_rowconfigure(0, weight=1)
        products_container.grid_columnconfigure(0, weight=1)
        
        # Create treeview for products with enhanced styling
        columns = ("SKU", "Name", "Stock", "Normal Price", "Workshop Price")
        self.products_tree = ttk.Treeview(products_container, columns=columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_sales_products_style(self.products_tree)
        
        # Define headings with optimized spacing
        column_widths = {"SKU": 120, "Name": 220, "Stock": 80, "Normal Price": 110, "Workshop Price": 120}
        for col in columns:
            self.products_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.products_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col != "Name" else "w", minwidth=70)
        
        # Add both scrollbars
        v_scrollbar = ttk.Scrollbar(products_container, orient="vertical", command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(products_container, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.products_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Add to cart button - positioned at bottom
        button_frame = ctk.CTkFrame(product_frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(5, 8))
        
        add_cart_button = ctk.CTkButton(
            button_frame,
            text="🛒 Add to Cart",
            command=lambda: self.add_to_cart(1),
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            width=200,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        add_cart_button.pack(pady=3)
        
        # Bind double-click to add to cart
        self.products_tree.bind("<Double-1>", lambda e: self.add_to_cart())
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        cart_frame = ctk.CTkScrollableFrame(parent, label_text="🛒 Shopping Cart")
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        
        
        # Cart items table - make responsive with minimum height
        cart_table_frame = ctk.CTkFrame(cart_frame)
        cart_table_frame.pack(fill="both", expand=True, padx=12, pady=(8, 10))
        
        # Create container for cart table
        cart_container = ctk.CTkFrame(cart_table_frame)
        cart_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for cart with enhanced styling
        cart_columns = ("Product", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_container, columns=cart_columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_cart_style(self.cart_tree)
        
        # Define headings with optimized spacing
        column_widths = {"Product": 160, "Qty": 60, "Price": 90, "Total": 90}
        for col in cart_columns:
            self.cart_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.cart_tree.column(col, width=column_widths.get(col, 100), anchor="center" if col != "Product" else "w", minwidth=60)
        
        # Add both scrollbars
        v_scrollbar = ttk.Scrollbar(cart_container, orient="vertical", command=self.cart_tree.yview)
        h_scrollbar = ttk.Scrollbar(cart_container, orient="horizontal", command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        cart_container.grid_rowconfigure(0, weight=1)
        cart_container.grid_columnconfigure(0, weight=1)
        
        # Cart actions
        actions_frame = ctk.CTkFrame(cart_frame)
        actions_frame.pack(fill="x", padx=12, pady=(8, 10))
        
        remove_button = ctk.CTkButton(
            actions_frame,
            text="❌ Remove Item",
            command=self.remove_from_cart,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        remove_button.pack(side="left", padx=(8, 5))
        
        clear_button = ctk.CTkButton(
            actions_frame,
            text="🗑 Clear Cart",
            command=self.clear_cart,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        clear_button.pack(side="left", padx=(5, 8))
        
        # No discount button here - moved to totals section
        
        # Discount section
        discount_frame = ctk.CTkFrame(cart_frame)
        discount_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        discount_header = ctk.CTkLabel(
            discount_frame,
            text="💸 Discount",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        discount_header.pack(pady=(8, 5))
        
        # Discount type selection
        discount_type_frame = ctk.CTkFrame(discount_frame)
        discount_type_frame.pack(fill="x", padx=8, pady=(0, 5))
        
        self.discount_type_var = tk.StringVar(value="amount")
        
        amount_radio = ctk.CTkRadioButton(
            discount_type_frame,
            text="Amount (Rs)",
            variable=self.discount_type_var,
            value="amount",
            command=self.on_discount_type_change,
            font=ctk.CTkFont(size=11)
        )
        amount_radio.pack(side="left", padx=(8, 15))
        
        percentage_radio = ctk.CTkRadioButton(
            discount_type_frame,
            text="Percentage (%)",
            variable=self.discount_type_var,
            value="percentage",
            command=self.on_discount_type_change,
            font=ctk.CTkFont(size=11)
        )
        percentage_radio.pack(side="left", padx=(0, 8))
        
        # Discount input section
        discount_input_frame = ctk.CTkFrame(discount_frame)
        discount_input_frame.pack(fill="x", padx=8, pady=(0, 5))
        
        self.discount_entry = ctk.CTkEntry(
            discount_input_frame,
            placeholder_text="Enter discount amount...",
            width=120,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.discount_entry.pack(side="left", padx=(8, 5), pady=5)
        
        # Bind entry changes to update totals
        self.discount_entry.bind('<KeyRelease>', self.on_discount_change)
        
        apply_discount_btn = ctk.CTkButton(
            discount_input_frame,
            text="Apply",
            command=self.apply_inline_discount,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        apply_discount_btn.pack(side="left", padx=(0, 5), pady=5)
        
        clear_discount_btn = ctk.CTkButton(
            discount_input_frame,
            text="Clear",
            command=self.clear_inline_discount,
            width=50,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        clear_discount_btn.pack(side="left", padx=(0, 8), pady=5)
        
        # Totals section
        totals_frame = ctk.CTkFrame(cart_frame)
        totals_frame.pack(fill="x", padx=10, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(
            totals_frame, 
            text="Subtotal: Rs0.00",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.subtotal_label.pack(pady=(8, 2))
        
        self.discount_label = ctk.CTkLabel(
            totals_frame, 
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.discount_label.pack(pady=2)
        
        self.total_label = ctk.CTkLabel(
            totals_frame, 
            text="Total: Rs0.00",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.total_label.pack(pady=(2, 8))
        
        # Process sale button
        process_button = ctk.CTkButton(
            cart_frame,
            text="💰 Process Sale",
            command=self.process_sale,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="green",
            hover_color="darkgreen"
        )
        process_button.pack(fill="x", padx=10, pady=8)
    
    def load_customers(self):
        """Load customers for dropdown"""
        try:
            customers = db.execute_query("SELECT customer_id, name, type FROM customers WHERE is_active = 1")
            customer_values = ["Walk-in Customer"]
            self.customers_data = {"Walk-in Customer": {"customer_id": None, "type": "Normal"}}
            
            for customer in customers:
                display_name = f"{customer['name']} ({customer['type']})"
                customer_values.append(display_name)
                self.customers_data[display_name] = {
                    "customer_id": customer['customer_id'],
                    "type": customer['type']
                }
            
            self.customer_dropdown.configure(values=customer_values)
            
        except Exception as e:
            print(f"Error loading customers: {e}")
    
    def load_products(self):
        """Load products for selection"""
        try:
            query = """
                SELECT p.product_id, p.sku, p.name, p.stock, p.price_normal, 
                       p.price_workshop, p.reorder_level
                FROM products p
                WHERE p.is_active = 1 AND p.stock > 0
                ORDER BY p.name
            """
            products = db.execute_query(query)
            
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Add products to tree
            for product in products:
                # Show stock status
                stock_display = f"{product['stock']}"
                if product['stock'] <= product['reorder_level']:
                    stock_display += " ⚠️"
                
                self.products_tree.insert("", "end", values=(
                    product['sku'],
                    product['name'],
                    stock_display,
                    f"Rs{product['price_normal']:.2f}",
                    f"Rs{product['price_workshop']:.2f}"
                ))
            
            self.all_products = products
            
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def filter_products(self, *args):
        """Filter products based on search"""
        search_term = self.search_var.get().lower()
        
        # Clear tree
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Filter and add matching products
        for product in self.all_products:
            if (search_term in product['name'].lower() or 
                search_term in product['sku'].lower()):
                
                stock_display = f"{product['stock']}"
                if product['stock'] <= product['reorder_level']:
                    stock_display += " ⚠️"
                
                self.products_tree.insert("", "end", values=(
                    product['sku'],
                    product['name'],
                    stock_display,
                    f"Rs{product['price_normal']:.2f}",
                    f"Rs{product['price_workshop']:.2f}"
                ))
    
    def on_customer_selected(self, customer_name):
        """Handle customer selection"""
        self.current_customer = self.customers_data.get(customer_name)
        self.update_cart_display()
    
    def add_to_cart(self, quantity=1):
        """Add selected product to cart with specified quantity"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
        
        # Get product details
        item_values = self.products_tree.item(selection[0], 'values')
        sku = item_values[0]
        
        # Find product in data
        product = None
        for p in self.all_products:
            if p['sku'] == sku:
                product = p
                break
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        # Validate quantity
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        if quantity > product['stock']:
            messagebox.showwarning("Warning", f"Only {product['stock']} units available. Adding {product['stock']} to cart.")
            quantity = product['stock']
        
        # Check if product already in cart
        existing_item = None
        for item in self.cart_items:
            if item['product_id'] == product['product_id']:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            if new_quantity > product['stock']:
                available = product['stock'] - existing_item['quantity']
                if available > 0:
                    messagebox.showwarning("Warning", f"Only {available} more units can be added.")
                    existing_item['quantity'] = product['stock']
                else:
                    messagebox.showwarning("Warning", "Maximum quantity already in cart.")
                    return
            else:
                existing_item['quantity'] = new_quantity
        else:
            # Add new item
            cart_item = {
                'product_id': product['product_id'],
                'sku': product['sku'],
                'name': product['name'],
                'quantity': quantity,
                'price_normal': product['price_normal'],
                'price_workshop': product['price_workshop'],
                'stock': product['stock']
            }
            self.cart_items.append(cart_item)
        
        self.update_cart_display()
    
    def add_custom_quantity(self):
        """Add product to cart with custom quantity"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
        
        # Get product details
        item_values = self.products_tree.item(selection[0], 'values')
        sku = item_values[0]
        
        # Find product in data
        product = None
        for p in self.all_products:
            if p['sku'] == sku:
                product = p
                break
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        # Ask for quantity
        quantity_str = tk.simpledialog.askstring(
            "Quantity", 
            f"Enter quantity for {product['name']}\n(Max available: {product['stock']})"
        )
        
        if quantity_str:
            try:
                quantity = int(quantity_str)
                self.add_to_cart(quantity)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        # Get selected item index
        item_index = self.cart_tree.index(selection[0])
        
        # Remove from cart
        if 0 <= item_index < len(self.cart_items):
            self.cart_items.pop(item_index)
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            if messagebox.askyesno("Confirm", "Clear all items from cart?"):
                self.cart_items = []
                self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display and totals"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        subtotal = 0
        customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
        
        # Add items to cart tree
        for item in self.cart_items:
            # Determine price based on customer type
            if customer_type == 'Workshop':
                unit_price = item['price_workshop']
            else:
                unit_price = item['price_normal']
            
            total_price = unit_price * item['quantity']
            subtotal += total_price
            
            self.cart_tree.insert("", "end", values=(
                item['name'][:20] + "..." if len(item['name']) > 20 else item['name'],
                item['quantity'],
                f"Rs{unit_price:.2f}",
                f"Rs{total_price:.2f}"
            ))
        
        # Calculate discount and final total
        discount_amount = 0
        if self.discount_amount > 0 or self.discount_percentage > 0:
            if self.discount_type == "amount":
                discount_amount = min(self.discount_amount, subtotal)
                print(f"Debug update_cart_display: Amount discount applied - {discount_amount}")
            else:  # percentage
                discount_amount = (subtotal * self.discount_percentage) / 100
                print(f"Debug update_cart_display: Percentage discount applied - {discount_amount} ({self.discount_percentage}%)")
        
        final_total = subtotal - discount_amount
        print(f"Debug update_cart_display: Subtotal={subtotal}, Discount={discount_amount}, Final Total={final_total}")
        
        # Update totals
        self.subtotal_label.configure(text=f"Subtotal: Rs{subtotal:.2f}")
        
        if discount_amount > 0:
            if self.discount_type == "amount":
                discount_text = f"Discount: -Rs{discount_amount:.2f}"
            else:
                discount_text = f"Discount ({self.discount_percentage:.1f}%): -Rs{discount_amount:.2f}"
            self.discount_label.configure(text=discount_text)
        else:
            self.discount_label.configure(text="")
        
        self.total_label.configure(text=f"Total: Rs{final_total:.2f}")
    
    def create_credit_payments_interface(self):
        """Create the Credit Payments tab — shows all outstanding credit sales."""
        self.credit_payments_frame = ctk.CTkFrame(self.content_container)

        # Outer scrollable container so everything is reachable
        scroll = ctk.CTkScrollableFrame(self.credit_payments_frame)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header_frame = ctk.CTkFrame(scroll)
        header_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="💳 Outstanding Credit Sales",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_credit_sales,
            width=100,
            height=35
        ).pack(side="right", padx=10, pady=10)

        # Summary bar
        self.credit_summary_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.credit_summary_label.pack(padx=10, pady=(0, 5))

        # Outstanding credit sales table (fixed height so it doesn't push history off screen)
        table_frame = ctk.CTkFrame(scroll)
        table_frame.pack(fill="x", padx=10, pady=0)

        table_container = ctk.CTkFrame(table_frame)
        table_container.pack(fill="x", padx=5, pady=5)
        table_container.grid_columnconfigure(0, weight=1)

        columns = ("Invoice", "Date", "Customer", "Total", "Paid", "Outstanding")
        self.credit_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=8)

        col_widths = {"Invoice": 160, "Date": 110, "Customer": 220,
                      "Total": 120, "Paid": 120, "Outstanding": 130}
        for col in columns:
            self.credit_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.credit_tree.column(col, width=col_widths.get(col, 120), anchor="center", minwidth=80)

        v_sb = ttk.Scrollbar(table_container, orient="vertical", command=self.credit_tree.yview)
        h_sb = ttk.Scrollbar(table_container, orient="horizontal", command=self.credit_tree.xview)
        self.credit_tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)

        self.credit_tree.grid(row=0, column=0, sticky="ew")
        v_sb.grid(row=0, column=1, sticky="ns")
        h_sb.grid(row=1, column=0, sticky="ew")

        # Action buttons
        actions_frame = ctk.CTkFrame(scroll)
        actions_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            actions_frame,
            text="💰 Record Payment",
            command=self.pay_credit_from_tab,
            width=150,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=5)

        # Double-click to pay
        self.credit_tree.bind("<Double-1>", lambda e: self.pay_credit_from_tab())

        # ── Payment History section ──────────────────────────────────────
        history_header = ctk.CTkFrame(scroll)
        history_header.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(
            history_header,
            text="📜 Credit Payment History",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=8)

        history_table_frame = ctk.CTkFrame(scroll)
        history_table_frame.pack(fill="x", padx=10, pady=(0, 10))

        history_container = ctk.CTkFrame(history_table_frame)
        history_container.pack(fill="x", padx=5, pady=5)
        history_container.grid_columnconfigure(0, weight=1)

        hist_cols = ("Date", "Invoice", "Customer", "Amount Paid", "Remaining After", "Recorded At")
        self.payment_history_tree = ttk.Treeview(history_container, columns=hist_cols, show="headings", height=8)

        hist_widths = {"Date": 100, "Invoice": 160, "Customer": 180,
                       "Amount Paid": 120, "Remaining After": 130, "Recorded At": 150}
        for col in hist_cols:
            self.payment_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.payment_history_tree.column(col, width=hist_widths.get(col, 120), anchor="center", minwidth=80)

        ph_vsb = ttk.Scrollbar(history_container, orient="vertical", command=self.payment_history_tree.yview)
        ph_hsb = ttk.Scrollbar(history_container, orient="horizontal", command=self.payment_history_tree.xview)
        self.payment_history_tree.configure(yscrollcommand=ph_vsb.set, xscrollcommand=ph_hsb.set)

        self.payment_history_tree.grid(row=0, column=0, sticky="ew")
        ph_vsb.grid(row=0, column=1, sticky="ns")
        ph_hsb.grid(row=1, column=0, sticky="ew")

    def load_credit_sales(self):
        """Load all outstanding credit sales into the Credit Payments tab."""
        try:
            query = """
                SELECT s.id as sale_id, s.invoice_number, s.sale_date,
                       s.total_amount, s.paid_amount,
                       (s.total_amount - s.paid_amount) as outstanding,
                       c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.status = 'credit' AND (s.total_amount - s.paid_amount) > 0
                ORDER BY s.sale_date ASC, s.id ASC
            """
            sales = db.execute_query(query)

            for item in self.credit_tree.get_children():
                self.credit_tree.delete(item)

            total_outstanding = 0
            for sale in sales:
                customer_name = sale['customer_name'] or "Walk-in Customer"
                outstanding = sale['outstanding']
                total_outstanding += outstanding
                self.credit_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    f"Rs{sale['total_amount']:.2f}",
                    f"Rs{sale['paid_amount']:.2f}",
                    f"Rs{outstanding:.2f}"
                ))

            self.all_credit_sales = sales
            count = len(sales)
            self.credit_summary_label.configure(
                text=f"{count} outstanding credit sale(s)  |  Total due: Rs{total_outstanding:.2f}"
            )

        except Exception as e:
            print(f"Error loading credit sales: {e}")
            messagebox.showerror("Error", f"Failed to load credit sales: {e}")

        # Also refresh payment history
        self.load_payment_history()

    def load_payment_history(self):
        """Load credit payment history into the history table."""
        try:
            query = """
                SELECT
                    p.payment_date,
                    s.invoice_number,
                    c.name as customer_name,
                    p.amount,
                    p.notes,
                    p.created_at
                FROM payments p
                LEFT JOIN customers c ON p.customer_id = c.customer_id
                LEFT JOIN sales s ON p.reference_number = s.invoice_number
                WHERE p.payment_type = 'credit_sale'
                ORDER BY p.created_at DESC
            """
            records = db.execute_query(query)

            for item in self.payment_history_tree.get_children():
                self.payment_history_tree.delete(item)

            for rec in records:
                customer_name = rec['customer_name'] or "Walk-in Customer"
                invoice = rec['invoice_number'] or "-"
                # notes stores "remaining:X" so we parse it
                remaining = "-"
                try:
                    if rec['notes'] and rec['notes'].startswith("remaining:"):
                        remaining = f"Rs{float(rec['notes'].split(':')[1]):.2f}"
                except Exception:
                    pass

                self.payment_history_tree.insert("", "end", values=(
                    rec['payment_date'],
                    invoice,
                    customer_name,
                    f"Rs{rec['amount']:.2f}",
                    remaining,
                    rec['created_at']
                ))

        except Exception as e:
            print(f"Error loading payment history: {e}")

    def pay_credit_from_tab(self):
        """Pay credit for a sale selected in the Credit Payments tab."""
        selection = self.credit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credit sale to pay.")
            return

        item_values = self.credit_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        selected_sale = None
        for sale in self.all_credit_sales:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        dialog = PaySaleCreditDialog(self.parent, selected_sale)
        if dialog.result:
            self.load_credit_sales()  # Refresh the tab

    def pay_credit_for_sale(self):
        """Pay off credit for a selected credit sale from Sales History."""
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to pay credit for.")
            return

        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        # Find the sale in loaded data
        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        # Check it is actually a credit sale with outstanding balance
        balance = selected_sale['total_amount'] - selected_sale['paid_amount']
        if balance <= 0:
            messagebox.showinfo("No Balance", f"Invoice {invoice_number} is already fully paid.")
            return

        if selected_sale['status'] != 'credit':
            messagebox.showinfo("Not a Credit Sale", f"Invoice {invoice_number} is not a credit sale.")
            return

        # Open the pay-credit dialog
        dialog = PaySaleCreditDialog(self.parent, selected_sale)
        if dialog.result:
            self.load_sales_history()  # Refresh the table

    def export_invoice(self):
        """Export a text invoice for the selected sale."""
        from tkinter import filedialog
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to export.")
            return

        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        # Load sale items
        try:
            items = db.execute_query("""
                SELECT si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """, (selected_sale['sale_id'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sale items: {e}")
            return

        # Build receipt text
        sep = "=" * 48
        thin = "-" * 48
        customer_name = selected_sale['customer_name'] or "Walk-in Customer"
        discount = selected_sale['discount'] or 0

        lines = [
            sep,
            "           INVENTORY PRO",
            "            Sales Invoice",
            sep,
            f"  Invoice : {selected_sale['invoice_number']}",
            f"  Date    : {selected_sale['sale_date']}",
            f"  Customer: {customer_name}",
            f"  Payment : {selected_sale['payment_method'].title()}",
            f"  Status  : {selected_sale['status'].title()}",
            thin,
            f"  {'Product':<22} {'Qty':>4} {'Price':>8} {'Total':>8}",
            thin,
        ]

        for item in items:
            name = item['name'][:22]
            lines.append(f"  {name:<22} {item['quantity']:>4} {item['unit_price']:>8.2f} {item['total']:>8.2f}")

        lines += [
            thin,
            f"  {'Subtotal':<30} Rs{selected_sale['total_amount'] + discount:>8.2f}",
        ]
        if discount > 0:
            lines.append(f"  {'Discount':<30} Rs{discount:>8.2f}")
        lines += [
            f"  {'TOTAL':<30} Rs{selected_sale['total_amount']:>8.2f}",
            f"  {'Paid':<30} Rs{selected_sale['paid_amount']:>8.2f}",
        ]
        balance = selected_sale['total_amount'] - selected_sale['paid_amount']
        if balance > 0:
            lines.append(f"  {'Balance Due':<30} Rs{balance:>8.2f}")
        lines += [
            sep,
            "        Thank you for your business!",
            sep,
            f"  Printed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        receipt_text = "\n".join(lines)

        # Ask where to save
        filename = filedialog.asksaveasfilename(
            title="Save Invoice",
            initialfile=f"{invoice_number}.txt",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(receipt_text)
            messagebox.showinfo("Invoice Exported", f"✅ Invoice saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def ask_credit_paid_amount(self, total_amount):
        """Show a dialog asking how much the customer is paying now for a credit sale.
        Returns the paid amount (float), or None if the user cancelled."""
        dialog = CreditPaymentDialog(self.parent, total_amount)
        return dialog.result

    def process_sale(self):
        """Process the sale transaction"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        try:
            # Generate invoice number
            today = datetime.now()
            base_number = f"INV-{today.strftime('%Y%m%d')}"
            
            # Find next number for today
            query = "SELECT COUNT(*) as count FROM sales WHERE invoice_number LIKE ?"
            result = db.execute_query(query, (f"{base_number}-%",))
            count = result[0]['count'] if result else 0
            
            invoice_number = f"{base_number}-{count + 1:03d}"
            
            # Calculate totals
            customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
            subtotal = 0
            
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                subtotal += unit_price * item['quantity']
            
            # Calculate discount
            discount_amount = 0
            if self.discount_amount > 0 or self.discount_percentage > 0:
                if self.discount_type == "amount":
                    discount_amount = min(self.discount_amount, subtotal)
                else:  # percentage
                    discount_amount = (subtotal * self.discount_percentage) / 100
            
            total_amount = subtotal - discount_amount
            
            # Create sale record
            customer_id = self.current_customer['customer_id'] if self.current_customer else None
            payment_method = self.payment_var.get().lower()
            
            if payment_method == 'cash':
                paid_amount = total_amount
                status = 'completed'
            else:
                # Ask how much the customer is paying now (partial or full credit)
                paid_amount = self.ask_credit_paid_amount(total_amount)
                if paid_amount is None:
                    return  # User cancelled
                if paid_amount >= total_amount:
                    paid_amount = total_amount
                    status = 'completed'
                else:
                    status = 'credit'
            sale_id = db.execute_insert("""
                INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method,
                                 subtotal, discount, total_amount, paid_amount, balance, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_number,
                customer_id,
                datetime.now().date(),
                payment_method,
                subtotal,
                discount_amount,
                total_amount,
                paid_amount,
                total_amount - paid_amount,
                status
            ))
            
            # Add sale items and update stock
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                
                total_price = unit_price * item['quantity']
                
                # Add sale item
                db.execute_insert("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sale_id,
                    item['product_id'],
                    item['quantity'],
                    unit_price,
                    total_price
                ))
                
                # Update stock
                db.execute_update("""
                    UPDATE products 
                    SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                """, (item['quantity'], item['product_id']))
            
            # Record sale transaction in payments table for complete history
            # Determine transaction type and notes based on payment status
            if payment_method == 'cash':
                # Cash sale - fully paid
                transaction_type = 'sale_cash'
                notes = f"Sale: Cash payment. Total: {total_amount:.2f}"
            elif status == 'completed':
                # Credit sale fully paid at time of purchase
                transaction_type = 'sale_credit_paid'
                notes = f"Sale: Credit fully paid. Total: {total_amount:.2f}"
            else:
                # Credit sale with balance remaining
                transaction_type = 'sale_credit'
                notes = f"Sale: Credit. Total: {total_amount:.2f}, Paid: {paid_amount:.2f}, Remaining: {total_amount - paid_amount:.2f}"
            
            db.execute_insert("""
                INSERT INTO payments (payment_type, customer_id, amount, 
                                    payment_method, reference_number, notes, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_type,
                customer_id,
                total_amount,  # Record the full sale amount
                payment_method,
                invoice_number,
                notes,
                datetime.now().date()
            ))
            
            # Record separate payment entry if there was an initial payment on credit sale
            if payment_method == 'credit' and paid_amount > 0:
                db.execute_insert("""
                    INSERT INTO payments (payment_type, customer_id, amount, 
                                        payment_method, reference_number, notes, payment_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    'payment',
                    customer_id,
                    paid_amount,
                    payment_method,
                    invoice_number,
                    f"Payment on invoice. Remaining: {total_amount - paid_amount:.2f}",
                    datetime.now().date()
                ))
            
            # Update customer credit balance if needed
            if payment_method == 'credit' and customer_id:
                db.execute_update("""
                    UPDATE customers 
                    SET credit_balance = credit_balance + ?
                    WHERE customer_id = ?
                """, (total_amount - paid_amount, customer_id))
            
            # Clear cart and refresh
            self.cart_items = []
            self.discount_amount = 0
            self.discount_type = "amount"
            self.discount_percentage = 0
            # Clear discount entry
            self.discount_entry.delete(0, tk.END)
            self.discount_type_var.set("amount")
            self.update_cart_display()
            self.load_products()
            
            messagebox.showinfo("Success", f"Sale completed successfully!\nInvoice: {invoice_number}")
            
        except Exception as e:
            print(f"Error processing sale: {e}")
            messagebox.showerror("Error", f"Failed to process sale: {e}")
    
    def apply_discount(self):
        """Open discount dialog and apply discount"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        # Calculate current subtotal
        subtotal = 0
        customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
        
        for item in self.cart_items:
            if customer_type == 'Workshop':
                unit_price = item['price_workshop']
            else:
                unit_price = item['price_normal']
            subtotal += unit_price * item['quantity']
        
        # Open discount dialog
        discount_dialog = DiscountDialog(self.parent, subtotal, self.discount_type, self.discount_amount, self.discount_percentage)
        
        if discount_dialog.result:
            self.discount_type = discount_dialog.discount_type
            self.discount_amount = discount_dialog.discount_amount
            self.discount_percentage = discount_dialog.discount_percentage
            self.update_cart_display()
            
            # Show confirmation message
            if self.discount_amount > 0 or self.discount_percentage > 0:
                if self.discount_type == "amount":
                    discount_text = f"Fixed discount of Rs{self.discount_amount:.2f} applied!"
                else:
                    discount_text = f"Percentage discount of {self.discount_percentage:.1f}% applied!"
                messagebox.showinfo("Discount Applied", discount_text)
            else:
                messagebox.showinfo("Discount Removed", "Discount has been removed from the cart.")
    
    def on_discount_type_change(self):
        """Handle discount type change in inline controls"""
        discount_type = self.discount_type_var.get()
        self.discount_type = discount_type
        
        # Update placeholder text
        if discount_type == "amount":
            self.discount_entry.configure(placeholder_text="Enter discount amount...")
        else:
            self.discount_entry.configure(placeholder_text="Enter discount percentage...")
        
        # Clear entry and reset discount
        self.discount_entry.delete(0, tk.END)
        self.discount_amount = 0
        self.discount_percentage = 0
        self.update_cart_display()
    
    def on_discount_change(self, event=None):
        """Handle discount entry changes for real-time preview"""
        # This method can be used for real-time preview if desired
        # For now, we'll keep it simple and only apply on button click
        pass
    
    def apply_inline_discount(self):
        """Apply discount from inline controls"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            print(f"Debug: Applying discount - Value: {discount_value}, Type: {discount_type}")
            
            if discount_value < 0:
                messagebox.showerror("Error", "Discount value cannot be negative.")
                return
            
            if discount_value == 0:
                messagebox.showwarning("Warning", "Please enter a discount value greater than 0.")
                return
            
            # Calculate current subtotal for validation
            subtotal = 0
            customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
            
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                subtotal += unit_price * item['quantity']
            
            print(f"Debug: Subtotal: {subtotal}, Customer type: {customer_type}")
            
            if discount_type == "amount":
                if discount_value > subtotal:
                    messagebox.showerror("Error", f"Discount amount cannot exceed subtotal (Rs{subtotal:.2f}).")
                    return
                self.discount_amount = discount_value
                self.discount_percentage = 0
                print(f"Debug: Applied amount discount: {self.discount_amount}")
            else:  # percentage
                if discount_value > 100:
                    messagebox.showerror("Error", "Discount percentage cannot exceed 100%.")
                    return
                self.discount_percentage = discount_value
                self.discount_amount = 0
                print(f"Debug: Applied percentage discount: {self.discount_percentage}%")
            
            self.discount_type = discount_type
            self.update_cart_display()
            
            # Show success message
            if discount_type == "amount":
                messagebox.showinfo("Discount Applied", f"Fixed discount of Rs{discount_value:.2f} applied!")
            else:
                messagebox.showinfo("Discount Applied", f"Percentage discount of {discount_value:.1f}% applied!")
            
        except ValueError as e:
            print(f"Debug: ValueError in apply_inline_discount: {e}")
            messagebox.showerror("Error", "Please enter a valid discount value.")
        except Exception as e:
            print(f"Debug: Unexpected error in apply_inline_discount: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def clear_inline_discount(self):
        """Clear discount from inline controls"""
        self.discount_amount = 0
        self.discount_percentage = 0
        self.discount_type = "amount"
        self.discount_entry.delete(0, tk.END)
        self.discount_type_var.set("amount")
        self.update_cart_display()


class CreditPaymentDialog:
    """Dialog to ask how much the customer is paying now on a credit sale."""
    def __init__(self, parent, total_amount):
        self.parent = parent
        self.total_amount = total_amount
        self.result = None  # None = cancelled, float = paid amount

        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("💳 Credit Sale - Payment Details")
        self.dialog.geometry("420x320")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 80, parent.winfo_rooty() + 80))

        # Prevent closing with X without handling
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._build_ui()
        self.dialog.wait_window()

    def _build_ui(self):
        main = ctk.CTkFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main,
            text="💳 Credit Sale",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 5))

        # Total amount info
        info_frame = ctk.CTkFrame(main, fg_color=("#dbeafe", "#1e3a5f"))
        info_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            info_frame,
            text=f"Total Bill:  Rs{self.total_amount:.2f}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        # Amount paid now
        ctk.CTkLabel(
            main,
            text="Amount paid now by customer (Rs):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=5)

        self.paid_entry = ctk.CTkEntry(
            main,
            placeholder_text="Enter 0 for full credit, or partial amount...",
            font=ctk.CTkFont(size=13),
            height=38
        )
        self.paid_entry.insert(0, "0")
        self.paid_entry.pack(fill="x", padx=5, pady=(5, 5))
        self.paid_entry.bind("<KeyRelease>", self._update_preview)

        # Live preview label
        self.preview_label = ctk.CTkLabel(
            main,
            text=f"Credit remaining: Rs{self.total_amount:.2f}",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B35"
        )
        self.preview_label.pack(pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="✅ Confirm Sale",
            command=self.on_confirm,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", fill="x", expand=True)

        # Focus on entry
        self.paid_entry.focus()
        self.paid_entry.select_range(0, "end")

    def _update_preview(self, event=None):
        """Update the credit remaining preview as user types."""
        try:
            paid = float(self.paid_entry.get() or "0")
            paid = max(0, min(paid, self.total_amount))
            remaining = self.total_amount - paid
            if remaining <= 0:
                self.preview_label.configure(
                    text="✅ Fully paid — no credit remaining.",
                    text_color="#4CAF50"
                )
            else:
                self.preview_label.configure(
                    text=f"Credit remaining: Rs{remaining:.2f}",
                    text_color="#FF6B35"
                )
        except ValueError:
            self.preview_label.configure(
                text="⚠️ Enter a valid number.",
                text_color="#FF6B35"
            )

    def on_confirm(self):
        """Validate and confirm the paid amount."""
        try:
            paid = float(self.paid_entry.get() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the paid amount.", parent=self.dialog)
            return

        if paid < 0:
            messagebox.showerror("Invalid Input", "Paid amount cannot be negative.", parent=self.dialog)
            return

        if paid > self.total_amount:
            messagebox.showerror(
                "Invalid Input",
                f"Paid amount (Rs{paid:.2f}) cannot exceed the total bill (Rs{self.total_amount:.2f}).",
                parent=self.dialog
            )
            return

        self.result = paid
        self.dialog.destroy()

    def on_cancel(self):
        """User cancelled — result stays None."""
        self.result = None
        self.dialog.destroy()


class PaySaleCreditDialog:
    """Dialog to record a payment against a specific credit sale."""
    def __init__(self, parent, sale_data):
        self.parent = parent
        self.sale_data = sale_data
        self.balance = sale_data['total_amount'] - sale_data['paid_amount']
        self.result = False

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Pay Credit - {sale_data['invoice_number']}")
        self.dialog.geometry("460x480")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 80, parent.winfo_rooty() + 80))
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._build_ui()
        self.dialog.wait_window()

    def _build_ui(self):
        main = ctk.CTkFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main,
            text="💰 Pay Credit Balance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 10))

        # Invoice info box
        info_frame = ctk.CTkFrame(main, fg_color=("#fef3c7", "#3b2f00"))
        info_frame.pack(fill="x", pady=(0, 15))

        try:
            customer_name = self.sale_data['customer_name'] or "Walk-in Customer"
        except (KeyError, IndexError):
            customer_name = "Walk-in Customer"
        ctk.CTkLabel(
            info_frame,
            text=f"Invoice:   {self.sale_data['invoice_number']}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(
            info_frame,
            text=f"Customer: {customer_name}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(
            info_frame,
            text=f"Total Bill:    Rs{self.sale_data['total_amount']:.2f}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(
            info_frame,
            text=f"Already Paid: Rs{self.sale_data['paid_amount']:.2f}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)

        self.balance_label = ctk.CTkLabel(
            info_frame,
            text=f"Outstanding:  Rs{self.balance:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.balance_label.pack(anchor="w", padx=15, pady=(2, 10))

        # Payment amount entry
        ctk.CTkLabel(
            main,
            text="Amount being paid now (Rs):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=5)

        self.pay_entry = ctk.CTkEntry(
            main,
            placeholder_text=f"Max: Rs{self.balance:.2f}",
            font=ctk.CTkFont(size=13),
            height=38
        )
        self.pay_entry.insert(0, f"{self.balance:.2f}")
        self.pay_entry.pack(fill="x", padx=5, pady=(5, 5))
        self.pay_entry.bind("<KeyRelease>", self._update_preview)

        # Live remaining label
        self.remaining_label = ctk.CTkLabel(
            main,
            text="After payment: Rs0.00 remaining",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.remaining_label.pack(pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="✅ Record Payment",
            command=self.on_confirm,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", fill="x", expand=True)

        self.pay_entry.focus()
        self.pay_entry.select_range(0, "end")
        self._update_preview()

    def _update_preview(self, event=None):
        try:
            paying = float(self.pay_entry.get() or "0")
            paying = max(0, min(paying, self.balance))
            remaining = self.balance - paying
            if remaining <= 0:
                self.remaining_label.configure(
                    text="✅ Fully paid after this payment!",
                    text_color="#4CAF50"
                )
            else:
                self.remaining_label.configure(
                    text=f"After payment: Rs{remaining:.2f} still remaining",
                    text_color="#FF6B35"
                )
        except ValueError:
            self.remaining_label.configure(
                text="⚠️ Enter a valid number.",
                text_color="#FF6B35"
            )

    def on_confirm(self):
        try:
            paying = float(self.pay_entry.get() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid payment amount.", parent=self.dialog)
            return

        if paying <= 0:
            messagebox.showerror("Invalid Input", "Payment amount must be greater than 0.", parent=self.dialog)
            return

        if paying > self.balance:
            messagebox.showerror(
                "Invalid Input",
                f"Payment (Rs{paying:.2f}) cannot exceed outstanding balance (Rs{self.balance:.2f}).",
                parent=self.dialog
            )
            return

        try:
            sale_id = self.sale_data['sale_id']
            new_paid = self.sale_data['paid_amount'] + paying
            new_balance = self.sale_data['total_amount'] - new_paid
            new_status = 'completed' if new_balance <= 0.01 else 'credit'

            # Update the sale record
            db.execute_update("""
                UPDATE sales
                SET paid_amount = ?, balance = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_paid, new_balance, new_status, sale_id))

            # Update customer credit balance if there is a customer
            customer_id = None
            sale_row = db.execute_query("SELECT customer_id FROM sales WHERE id = ?", (sale_id,))
            if sale_row:
                customer_id = sale_row[0]['customer_id']

            if customer_id:
                db.execute_update("""
                    UPDATE customers
                    SET credit_balance = credit_balance - ?
                    WHERE customer_id = ?
                """, (paying, customer_id))

            # Save a record in the payments table for history
            db.execute_insert("""
                INSERT INTO payments (payment_type, customer_id, amount, payment_method,
                                      reference_number, notes, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'credit_sale',
                customer_id,
                paying,
                'cash',
                self.sale_data['invoice_number'],
                f"remaining:{new_balance:.2f}",
                datetime.now().strftime("%Y-%m-%d")
            ))

            if new_status == 'completed':
                messagebox.showinfo(
                    "Payment Recorded",
                    f"Rs{paying:.2f} recorded.\nInvoice {self.sale_data['invoice_number']} is now FULLY PAID!",
                    parent=self.dialog
                )
            else:
                messagebox.showinfo(
                    "Payment Recorded",
                    f"Rs{paying:.2f} recorded.\nRemaining balance: Rs{new_balance:.2f}",
                    parent=self.dialog
                )

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            print(f"Error recording credit payment: {e}")
            messagebox.showerror("Error", f"Failed to record payment: {e}", parent=self.dialog)

    def on_cancel(self):
        self.result = False
        self.dialog.destroy()


class SaleDetailsDialog:
    def __init__(self, parent, sale_data):
        self.parent = parent
        self.sale_data = sale_data
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Sale Details - {sale_data['invoice_number']}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_details_view()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_details_view(self):
        """Create the details view"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header information
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Invoice details
        invoice_label = ctk.CTkLabel(
            header_frame,
            text=f"Invoice: {self.sale_data['invoice_number']}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        invoice_label.pack(pady=10)
        
        details_frame = ctk.CTkFrame(header_frame)
        details_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Sale information
        discount_amount = self.sale_data['discount'] if 'discount' in self.sale_data.keys() else 0
        info_text = f"""
        Date: {self.sale_data['sale_date']}
        Customer: {self.sale_data['customer_name'] or 'Walk-in Customer'}
        Payment Method: {self.sale_data['payment_method'].title()}
        Status: {self.sale_data['status'].title()}
        Discount Applied: Rs{discount_amount:.2f}{' (None)' if discount_amount == 0 else ''}
        Total Amount: Rs{self.sale_data['total_amount']:.2f}
        """
        
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=10)
        
        # Sale items
        items_label = ctk.CTkLabel(
            main_frame,
            text="Sale Items:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        items_label.pack(anchor="w", pady=(0, 10))
        
        # Items table
        items_frame = ctk.CTkFrame(main_frame)
        items_frame.pack(fill="both", expand=True)
        
        # Load and display sale items
        self.load_sale_items(items_frame)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.dialog.destroy,
            width=100,
            height=35
        )
        close_btn.pack(pady=(20, 0))
    
    def load_sale_items(self, parent):
        """Load and display sale items"""
        try:
            query = """
                SELECT si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """
            items = db.execute_query(query, (self.sale_data['sale_id'],))
            
            # Create treeview for items with enhanced styling
            columns = ("SKU", "Product", "Quantity", "Unit Price", "Total")
            items_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
            
            # Apply centralized styling
            table_styles.apply_sale_details_style(items_tree)
            
            # Define headings and column widths - bigger columns
            column_widths = {"SKU": 120, "Product": 220, "Quantity": 100, 
                           "Unit Price": 120, "Total": 120}
            
            for col in columns:
                items_tree.heading(col, text=f"  {col}  ", anchor="center")
                items_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col != "Product" else "w", minwidth=80)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=items_tree.yview)
            items_tree.configure(yscrollcommand=v_scrollbar.set)
            
            # Pack table and scrollbar
            items_tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            
            # Add items to tree
            for item in items:
                items_tree.insert("", "end", values=(
                    item['sku'],
                    item['name'],
                    item['quantity'],
                    f"Rs{item['unit_price']:.2f}",
                    f"Rs{item['total']:.2f}"
                ))
                
        except Exception as e:
            print(f"Error loading sale items: {e}")
            error_label = ctk.CTkLabel(
                parent,
                text="Error loading sale items",
                font=ctk.CTkFont(size=12)
            )
            error_label.pack(pady=20)


class DiscountDialog:
    def __init__(self, parent, subtotal, current_discount_type="amount", current_discount_amount=0, current_discount_percentage=0):
        self.parent = parent
        self.subtotal = subtotal
        self.discount_type = current_discount_type
        self.discount_amount = current_discount_amount
        self.discount_percentage = current_discount_percentage
        self.result = False
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Apply Discount")
        self.dialog.geometry("750x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        # Make dialog resizable
        self.dialog.minsize(450, 400)
        
        # Prevent closing with X button without handling
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_discount_interface()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_discount_interface(self):
        """Create the discount interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="💸 Apply Discount",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Current subtotal display
        subtotal_frame = ctk.CTkFrame(main_frame)
        subtotal_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            subtotal_frame,
            text=f"Current Subtotal: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Discount type selection
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            type_frame,
            text="Discount Type:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Radio buttons for discount type
        self.discount_type_var = tk.StringVar(value=self.discount_type)
        
        amount_radio = ctk.CTkRadioButton(
            type_frame,
            text="Fixed Amount (Rs)",
            variable=self.discount_type_var,
            value="amount",
            command=self.on_discount_type_changed
        )
        amount_radio.pack(anchor="w", padx=30, pady=5)
        
        percentage_radio = ctk.CTkRadioButton(
            type_frame,
            text="Percentage (%)",
            variable=self.discount_type_var,
            value="percentage",
            command=self.on_discount_type_changed
        )
        percentage_radio.pack(anchor="w", padx=30, pady=(5, 10))
        
        # Discount value input
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=(0, 15))
        
        self.discount_label = ctk.CTkLabel(
            input_frame,
            text="Discount Amount (Rs):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.discount_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.discount_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter discount value...",
            font=ctk.CTkFont(size=12)
        )
        self.discount_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Set initial values
        if self.discount_type == "amount" and self.discount_amount > 0:
            self.discount_entry.insert(0, str(self.discount_amount))
        elif self.discount_type == "percentage" and self.discount_percentage > 0:
            self.discount_entry.insert(0, str(self.discount_percentage))
        
        # Bind entry changes to update preview
        self.discount_entry.bind('<KeyRelease>', self.update_preview)
        
        # Preview section
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            preview_frame,
            text="Preview:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.preview_subtotal = ctk.CTkLabel(
            preview_frame,
            text=f"Subtotal: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=12)
        )
        self.preview_subtotal.pack(anchor="w", padx=30, pady=2)
        
        self.preview_discount = ctk.CTkLabel(
            preview_frame,
            text="Discount: Rs0.00",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B35"
        )
        self.preview_discount.pack(anchor="w", padx=30, pady=2)
        
        self.preview_total = ctk.CTkLabel(
            preview_frame,
            text=f"Final Total: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        )
        self.preview_total.pack(anchor="w", padx=30, pady=(2, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Create a grid layout for better button spacing
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=40,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cancel_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Remove Discount",
            command=self.on_clear,
            width=140,
            height=40,
            fg_color="#FF6B35",
            hover_color="#E55A2B",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        clear_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="✅ Apply Discount",
            command=self.on_apply,
            width=130,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        apply_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        # Update interface based on current type
        self.on_discount_type_changed()
        self.update_preview()
    
    def on_discount_type_changed(self):
        """Handle discount type change"""
        discount_type = self.discount_type_var.get()
        
        if discount_type == "amount":
            self.discount_label.configure(text="Discount Amount (Rs):")
            self.discount_entry.configure(placeholder_text="Enter amount...")
        else:
            self.discount_label.configure(text="Discount Percentage (%):")
            self.discount_entry.configure(placeholder_text="Enter percentage...")
        
        # Clear entry when switching types
        if discount_type != self.discount_type:
            self.discount_entry.delete(0, tk.END)
        
        self.discount_type = discount_type
        self.update_preview()
    
    def update_preview(self, event=None):
        """Update the discount preview"""
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                discount_amount = min(discount_value, self.subtotal)  # Can't discount more than subtotal
                discount_text = f"Discount: -Rs{discount_amount:.2f}"
            else:  # percentage
                discount_percentage = min(discount_value, 100)  # Max 100%
                discount_amount = (self.subtotal * discount_percentage) / 100
                discount_text = f"Discount ({discount_percentage:.1f}%): -Rs{discount_amount:.2f}"
            
            final_total = self.subtotal - discount_amount
            
            self.preview_discount.configure(text=discount_text)
            self.preview_total.configure(text=f"Final Total: Rs{final_total:.2f}")
            
        except ValueError:
            # Invalid input
            self.preview_discount.configure(text="Discount: Rs0.00")
            self.preview_total.configure(text=f"Final Total: Rs{self.subtotal:.2f}")
    
    def on_apply(self):
        """Apply the discount"""
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            if discount_value < 0:
                messagebox.showerror("Error", "Discount value cannot be negative.")
                return
            
            if discount_type == "amount":
                if discount_value > self.subtotal:
                    messagebox.showerror("Error", f"Discount amount cannot exceed subtotal (Rs{self.subtotal:.2f}).")
                    return
                self.discount_amount = discount_value
                self.discount_percentage = 0
            else:  # percentage
                if discount_value > 100:
                    messagebox.showerror("Error", "Discount percentage cannot exceed 100%.")
                    return
                self.discount_percentage = discount_value
                self.discount_amount = (self.subtotal * discount_value) / 100
            
            self.discount_type = discount_type
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid discount value.")
    
    def on_clear(self):
        """Remove discount"""
        self.discount_amount = 0
        self.discount_percentage = 0
        self.discount_type = "amount"
        self.result = True
        self.dialog.destroy()
    
    def on_cancel(self):
        """Cancel discount dialog"""
        self.result = False
        self.dialog.destroy()
