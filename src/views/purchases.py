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

class PurchasesView:
    def __init__(self, parent):
        self.parent = parent
        self.purchase_items = []
        self.current_supplier = None
        self.all_products = []  # Initialize products list
        self.suppliers_data = {}  # Initialize suppliers data
        self.create_purchases_interface()
        self.load_suppliers()
        self.load_products()
    
    def create_purchases_interface(self):
        """Create the purchases management interface"""
        # Main container with gradient background
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame, height=80, corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Tab buttons with improved styling
        tab_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        tab_frame.pack(side="left", padx=15, pady=15)
        
        self.new_purchase_btn = ctk.CTkButton(
            tab_frame,
            text="🛒 New Purchase",
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            command=lambda: self.switch_tab("new_purchase")
        )
        self.new_purchase_btn.pack(side="left", padx=(0, 15))
        
        self.purchase_history_btn = ctk.CTkButton(
            tab_frame,
            text="📋 Purchase History",
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            corner_radius=10,
            command=lambda: self.switch_tab("purchase_history")
        )
        self.purchase_history_btn.pack(side="left")
        
        # Current tab tracking
        self.current_tab = "new_purchase"
        
        # Content container
        self.content_container = ctk.CTkFrame(main_frame)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create both interfaces
        self.create_new_purchase_interface()
        self.create_purchase_history_interface()
        
        # Show new purchase interface by default
        self.switch_tab("new_purchase")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab = tab_name
        
        # Update button styles
        active_color = ("#1f538d", "#14375e")
        inactive_color = ("gray85", "gray25")
        inactive_text_color = ("gray40", "gray80")
        
        if tab_name == "new_purchase":
            self.new_purchase_btn.configure(fg_color=active_color, text_color="white")
            self.purchase_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        else:
            self.new_purchase_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.purchase_history_btn.configure(fg_color=active_color, text_color="white")
        
        # Show/hide appropriate interface
        if tab_name == "new_purchase":
            self.new_purchase_frame.pack(fill="both", expand=True)
            self.purchase_history_frame.pack_forget()
        else:
            self.new_purchase_frame.pack_forget()
            self.purchase_history_frame.pack(fill="both", expand=True)
            self.load_purchase_history()
    
    def create_new_purchase_interface(self):
        """Create the new purchase interface"""
        self.new_purchase_frame = ctk.CTkFrame(self.content_container, corner_radius=12)
        
        # Supplier selection header with improved styling
        header_frame = ctk.CTkFrame(self.new_purchase_frame, height=80, corner_radius=10, fg_color=("#f0f0f0", "#2b2b2b"))
        header_frame.pack(fill="x", padx=15, pady=15)
        
        # Supplier selection with icon
        supplier_icon = ctk.CTkLabel(header_frame, text="🏢", font=ctk.CTkFont(size=20))
        supplier_icon.pack(side="left", padx=(15, 5), pady=15)
        
        supplier_label = ctk.CTkLabel(header_frame, text="Supplier:", font=ctk.CTkFont(size=14, weight="bold"))
        supplier_label.pack(side="left", padx=(0, 8), pady=15)
        
        self.supplier_var = tk.StringVar(value="Select Supplier...")
        self.supplier_dropdown = ctk.CTkOptionMenu(
            header_frame, 
            variable=self.supplier_var,
            command=self.on_supplier_selected,
            width=220,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.supplier_dropdown.pack(side="left", padx=8, pady=15)
        
        # Payment method with icon
        payment_icon = ctk.CTkLabel(header_frame, text="💳", font=ctk.CTkFont(size=18))
        payment_icon.pack(side="left", padx=(20, 5), pady=15)
        
        payment_label = ctk.CTkLabel(header_frame, text="Payment:", font=ctk.CTkFont(size=14, weight="bold"))
        payment_label.pack(side="left", padx=(0, 8), pady=15)
        
        self.payment_var = tk.StringVar(value="Cash")
        payment_dropdown = ctk.CTkOptionMenu(
            header_frame,
            variable=self.payment_var,
            values=["Cash", "Credit"],
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        payment_dropdown.pack(side="left", padx=8, pady=15)
        
        # Expected delivery date with icon
        delivery_icon = ctk.CTkLabel(header_frame, text="📅", font=ctk.CTkFont(size=18))
        delivery_icon.pack(side="left", padx=(20, 5), pady=15)
        
        delivery_label = ctk.CTkLabel(header_frame, text="Expected Delivery:", font=ctk.CTkFont(size=14, weight="bold"))
        delivery_label.pack(side="left", padx=(0, 8), pady=15)
        
        self.delivery_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="YYYY-MM-DD",
            width=140,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.delivery_entry.pack(side="left", padx=8, pady=15)
        
        # Content area with two columns and improved spacing
        content_frame = ctk.CTkFrame(self.new_purchase_frame, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        content_frame.grid_columnconfigure(0, weight=4)  # Products section 
        content_frame.grid_columnconfigure(1, weight=6)  # Purchase order section gets more space
        
        # Left side - Product selection
        self.create_product_selection(content_frame)
        
        # Right side - Purchase order items
        self.create_purchase_order_section(content_frame)
    
    def create_purchase_history_interface(self):
        """Create the purchase history interface"""
        self.purchase_history_frame = ctk.CTkFrame(self.content_container)
        
        # Header with search and filters
        header_frame = ctk.CTkFrame(self.purchase_history_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(header_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.purchase_search_var = tk.StringVar()
        self.purchase_search_var.trace('w', self.filter_purchase_history)
        search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.purchase_search_var,
            placeholder_text="Search by PO number or supplier...",
            width=300
        )
        search_entry.pack(side="left", padx=5, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_purchase_history,
            width=100,
            height=35
        )
        refresh_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Purchase history table
        table_frame = ctk.CTkFrame(self.purchase_history_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for purchase history with enhanced styling
        columns = ("PO Number", "Date", "Supplier", "Items", "Total", "Status", "Expected Delivery")
        self.purchase_history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_purchase_history_style(self.purchase_history_tree)
        
        # Define headings and column widths - bigger columns
        column_widths = {"PO Number": 150, "Date": 120, "Supplier": 180, "Items": 80, 
                        "Total": 120, "Status": 100, "Expected Delivery": 150}
        
        for col in columns:
            self.purchase_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.purchase_history_tree.column(col, width=column_widths.get(col, 120), anchor="center", minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.purchase_history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.purchase_history_tree.xview)
        self.purchase_history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.purchase_history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self.purchase_history_frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        view_details_btn = ctk.CTkButton(
            actions_frame,
            text="👁️ View Details",
            command=self.view_purchase_details,
            width=120,
            height=35
        )
        view_details_btn.pack(side="left", padx=5)
        
        receive_btn = ctk.CTkButton(
            actions_frame,
            text="📦 Mark as Received",
            command=self.mark_as_received,
            width=140,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        )
        receive_btn.pack(side="left", padx=5)
        
        # Double-click to view details
        self.purchase_history_tree.bind("<Double-1>", lambda e: self.view_purchase_details())
    
    def create_product_selection(self, parent):
        """Create product selection area"""
        # Use regular frame with proper grid layout
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
        columns = ("SKU", "Name", "Current Stock", "Reorder Level", "Cost Price")
        self.products_tree = ttk.Treeview(products_container, columns=columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_purchase_products_style(self.products_tree)
        
        # Define headings with better spacing
        column_widths = {"SKU": 120, "Name": 200, "Current Stock": 100, "Reorder Level": 100, "Cost Price": 100}
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
        
        # Add to purchase order buttons
        button_frame = ctk.CTkFrame(product_frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(5, 8))
        
        add_one_button = ctk.CTkButton(
            button_frame,
            text="➕ Add 1 to PO",
            command=lambda: self.add_to_purchase_order(1),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            width=140,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        add_one_button.pack(side="left", padx=(8, 5), pady=5)
        
        add_custom_button = ctk.CTkButton(
            button_frame,
            text="📝 Add Custom Qty",
            command=self.add_custom_quantity_po,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            width=140,
            corner_radius=8,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        add_custom_button.pack(side="left", padx=(5, 8), pady=5)
        
        # Bind double-click to add 1 to purchase order
        self.products_tree.bind("<Double-1>", lambda e: self.add_to_purchase_order(1))
    
    def create_purchase_order_section(self, parent):
        """Create purchase order section"""
        po_frame = ctk.CTkScrollableFrame(parent, label_text="📋 Purchase Order Items")
        po_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        
        # Purchase order items table - make responsive
        po_table_frame = ctk.CTkFrame(po_frame)
        po_table_frame.pack(fill="both", expand=True, padx=12, pady=(8, 10))
        
        # Create container for purchase order table
        po_container = ctk.CTkFrame(po_table_frame)
        po_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for purchase order with enhanced styling
        po_columns = ("Product", "Qty", "Unit Cost", "Total")
        self.po_tree = ttk.Treeview(po_container, columns=po_columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_purchase_order_style(self.po_tree)
        
        # Define headings with better spacing
        column_widths = {"Product": 160, "Qty": 60, "Unit Cost": 90, "Total": 90}
        for col in po_columns:
            self.po_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.po_tree.column(col, width=column_widths.get(col, 100), anchor="center" if col != "Product" else "w", minwidth=60)
        
        # Add both scrollbars
        v_scrollbar = ttk.Scrollbar(po_container, orient="vertical", command=self.po_tree.yview)
        h_scrollbar = ttk.Scrollbar(po_container, orient="horizontal", command=self.po_tree.xview)
        self.po_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.po_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        po_container.grid_rowconfigure(0, weight=1)
        po_container.grid_columnconfigure(0, weight=1)
        
        # Purchase order actions
        actions_frame = ctk.CTkFrame(po_frame)
        actions_frame.pack(fill="x", padx=12, pady=(8, 10))
        
        remove_button = ctk.CTkButton(
            actions_frame,
            text="❌ Remove Item",
            command=self.remove_from_purchase_order,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        remove_button.pack(side="left", padx=(8, 5))
        
        clear_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Clear All",
            command=self.clear_purchase_order,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        clear_button.pack(side="left", padx=(5, 8))
        
        # Totals section
        totals_frame = ctk.CTkFrame(po_frame)
        totals_frame.pack(fill="x", padx=10, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(
            totals_frame, 
            text="Subtotal: Rs0.00",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.subtotal_label.pack(pady=(8, 2))
        
        self.total_label = ctk.CTkLabel(
            totals_frame, 
            text="Total: Rs0.00",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.total_label.pack(pady=(2, 8))
        
        # Create purchase order button
        create_po_button = ctk.CTkButton(
            po_frame,
            text="📋 Create Purchase Order",
            command=self.create_purchase_order,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="green",
            hover_color="darkgreen"
        )
        create_po_button.pack(fill="x", padx=10, pady=8)
    
    def load_suppliers(self):
        """Load suppliers for dropdown"""
        try:
            suppliers = db.execute_query("SELECT supplier_id, name FROM suppliers WHERE is_active = 1")
            supplier_values = ["Select Supplier..."]
            self.suppliers_data = {"Select Supplier...": {"supplier_id": None}}
            
            for supplier in suppliers:
                supplier_values.append(supplier['name'])
                self.suppliers_data[supplier['name']] = {
                    "supplier_id": supplier['supplier_id']
                }
            
            self.supplier_dropdown.configure(values=supplier_values)
            
        except Exception as e:
            print(f"Error loading suppliers: {e}")
    
    def load_products(self):
        """Load products for selection"""
        try:
            query = """
                SELECT p.product_id, p.sku, p.name, p.stock, p.cost_price, p.reorder_level
                FROM products p
                WHERE p.is_active = 1
                ORDER BY p.name
            """
            products = db.execute_query(query)
            
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Add products to tree
            for product in products:
                # Highlight products that need restocking
                stock_display = f"{product['stock']}"
                if product['stock'] <= product['reorder_level']:
                    stock_display += " ⚠️"
                
                self.products_tree.insert("", "end", values=(
                    product['sku'],
                    product['name'],
                    stock_display,
                    product['reorder_level'],
                    f"Rs{product['cost_price']:.2f}" if product['cost_price'] else "N/A"
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
                    product['reorder_level'],
                    f"Rs{product['cost_price']:.2f}" if product['cost_price'] else "N/A"
                ))
    
    def on_supplier_selected(self, supplier_name):
        """Handle supplier selection"""
        self.current_supplier = self.suppliers_data.get(supplier_name)
        self.update_purchase_order_display()
    
    def add_to_purchase_order(self, quantity=1, unit_cost=None):
        """Add selected product to purchase order with specified quantity"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
        
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier first.")
            return
        
        # Debug: Check if we have products data
        if not hasattr(self, 'all_products') or not self.all_products:
            messagebox.showerror("Error", "Products data not loaded. Please refresh the page.")
            return
        
        # Get product details
        try:
            item_values = self.products_tree.item(selection[0], 'values')
            if not item_values:
                messagebox.showerror("Error", "Unable to get product details.")
                return
            
            sku = item_values[0]
            
            # Find product in data
            product = None
            for p in self.all_products:
                if p['sku'] == sku:
                    product = p
                    break
            
            if not product:
                # Try to reload products and search again
                self.load_products()
                for p in self.all_products:
                    if p['sku'] == sku:
                        product = p
                        break
                
                if not product:
                    messagebox.showerror("Error", f"Product with SKU '{sku}' not found in database.")
                    return
        
        except Exception as e:
            messagebox.showerror("Error", f"Error getting product details: {e}")
            return
        
        # Use the current cost price or provided unit cost
        if unit_cost is None:
            unit_cost = product['cost_price'] if product['cost_price'] else 0.0
        
        # Validate quantity
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        
        # Check if product already in purchase order
        existing_item = None
        for item in self.purchase_items:
            if item['product_id'] == product['product_id']:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity and cost
            existing_item['quantity'] += quantity
            existing_item['unit_cost'] = unit_cost
        else:
            # Add new item
            po_item = {
                'product_id': product['product_id'],
                'sku': product['sku'],
                'name': product['name'],
                'quantity': quantity,
                'unit_cost': unit_cost
            }
            self.purchase_items.append(po_item)
        
        self.update_purchase_order_display()
    
    def add_custom_quantity_po(self):
        """Add product to purchase order with custom quantity and cost"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
        
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier first.")
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
            f"Enter quantity for {product['name']}"
        )
        
        if quantity_str:
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                
                # Ask for unit cost
                default_cost = product['cost_price'] if product['cost_price'] else 0.0
                cost_str = tk.simpledialog.askstring(
                    "Unit Cost", 
                    f"Enter unit cost for {product['name']}\n(Current cost: Rs{default_cost:.2f})",
                    initialvalue=str(default_cost)
                )
                
                if cost_str:
                    try:
                        unit_cost = float(cost_str)
                        if unit_cost < 0:
                            messagebox.showerror("Error", "Unit cost cannot be negative")
                            return
                        
                        self.add_to_purchase_order(quantity, unit_cost)
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid cost")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
    
    def remove_from_purchase_order(self):
        """Remove selected item from purchase order"""
        selection = self.po_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        # Get selected item index
        item_index = self.po_tree.index(selection[0])
        
        # Remove from purchase order
        if 0 <= item_index < len(self.purchase_items):
            self.purchase_items.pop(item_index)
            self.update_purchase_order_display()
    
    def clear_purchase_order(self):
        """Clear all items from purchase order"""
        if self.purchase_items:
            if messagebox.askyesno("Confirm", "Clear all items from purchase order?"):
                self.purchase_items = []
                self.update_purchase_order_display()
    
    def update_purchase_order_display(self):
        """Update purchase order display and totals"""
        # Clear purchase order tree
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        
        subtotal = 0
        
        # Add items to purchase order tree
        for item in self.purchase_items:
            total_cost = item['unit_cost'] * item['quantity']
            subtotal += total_cost
            
            self.po_tree.insert("", "end", values=(
                item['name'][:20] + "..." if len(item['name']) > 20 else item['name'],
                item['quantity'],
                f"Rs{item['unit_cost']:.2f}",
                f"Rs{total_cost:.2f}"
            ))
        
        # Update totals
        self.subtotal_label.configure(text=f"Subtotal: Rs{subtotal:.2f}")
        self.total_label.configure(text=f"Total: Rs{subtotal:.2f}")
    
    def create_purchase_order(self):
        """Create the purchase order"""
        if not self.purchase_items:
            messagebox.showwarning("Warning", "Purchase order is empty. Add items first.")
            return
        
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier.")
            return
        
        try:
            # Generate PO number
            today = datetime.now()
            base_number = f"PO-{today.strftime('%Y%m%d')}"
            
            # Find next number for today
            query = "SELECT COUNT(*) as count FROM purchases WHERE invoice_number LIKE ?"
            result = db.execute_query(query, (f"{base_number}-%",))
            count = result[0]['count'] if result else 0
            
            po_number = f"{base_number}-{count + 1:03d}"
            
            # Calculate totals
            subtotal = sum(item['unit_cost'] * item['quantity'] for item in self.purchase_items)
            
            # Get expected delivery date
            expected_delivery = self.delivery_entry.get() or None
            if expected_delivery:
                try:
                    # Validate date format
                    datetime.strptime(expected_delivery, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                    return
            
            # Create purchase record
            purchase_id = db.execute_insert("""
                INSERT INTO purchases (invoice_number, supplier_id, purchase_date,
                                     payment_method, subtotal, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                po_number,
                self.current_supplier['supplier_id'],
                datetime.now().date(),
                self.payment_var.get().lower(),
                subtotal,
                subtotal,
                'pending',
                f"Expected delivery: {expected_delivery}" if expected_delivery else None
            ))
            
            # Add purchase items
            for item in self.purchase_items:
                total_cost = item['unit_cost'] * item['quantity']
                
                db.execute_insert("""
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    item['product_id'],
                    item['quantity'],
                    item['unit_cost'],
                    total_cost
                ))
            
            # Clear purchase order and refresh
            self.purchase_items = []
            self.update_purchase_order_display()
            self.supplier_var.set("Select Supplier...")
            self.current_supplier = None
            self.delivery_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Purchase order created successfully!\nPO Number: {po_number}")
            
        except Exception as e:
            print(f"Error creating purchase order: {e}")
            messagebox.showerror("Error", f"Failed to create purchase order: {e}")
    
    def load_purchase_history(self):
        """Load purchase history data"""
        try:
            query = """
                SELECT p.id as purchase_id, p.invoice_number as po_number, p.purchase_date, p.notes,
                       p.total_amount, p.status, s.name as supplier_name,
                       COUNT(pi.id) as item_count
                FROM purchases p
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN purchase_items pi ON p.id = pi.purchase_id
                GROUP BY p.id
                ORDER BY p.purchase_date DESC
            """
            purchases = db.execute_query(query)
            
            # Clear existing items
            for item in self.purchase_history_tree.get_children():
                self.purchase_history_tree.delete(item)
            
            # Add purchases to tree
            for purchase in purchases:
                supplier_name = purchase['supplier_name'] or "Unknown Supplier"
                status = purchase['status'].title()
                # Extract expected delivery from notes if available
                notes = purchase['notes'] or ""
                expected_delivery = "Not specified"
                if "Expected delivery:" in notes:
                    try:
                        expected_delivery = notes.split("Expected delivery: ")[1].strip()
                    except:
                        expected_delivery = "Not specified"
                
                self.purchase_history_tree.insert("", "end", values=(
                    purchase['po_number'],
                    purchase['purchase_date'],
                    supplier_name,
                    purchase['item_count'],
                    f"Rs{purchase['total_amount']:.2f}",
                    status,
                    expected_delivery
                ))
            
            self.all_purchase_data = purchases
            
        except Exception as e:
            print(f"Error loading purchase history: {e}")
            messagebox.showerror("Error", f"Failed to load purchase history: {e}")
    
    def filter_purchase_history(self, *args):
        """Filter purchase history based on search"""
        pass  # Simplified for now
    
    def view_purchase_details(self):
        """View detailed information about a selected purchase"""
        messagebox.showinfo("Info", "Purchase details feature coming soon!")
    
    def mark_as_received(self):
        """Mark selected purchase order as received"""
        messagebox.showinfo("Info", "Mark as received feature coming soon!")
    
    def show_add_product_dialog(self, product):
        """Show custom dialog for adding product to purchase order"""
        dialog = AddProductDialog(self.parent, product)
        return dialog.result


class AddProductDialog:
    def __init__(self, parent, product):
        self.parent = parent
        self.product = product
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Add {product['name']} to Purchase Order")
        self.dialog.geometry("500x500")  # Increased height for better visibility
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)  # Make dialog non-resizable
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 50))
        
        self.create_dialog_content()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_dialog_content(self):
        """Create the dialog content"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product info header
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#e3f2fd", "#1565c0"))
        header_frame.pack(fill="x", padx=15, pady=(15, 20))
        
        product_icon = ctk.CTkLabel(header_frame, text="📦", font=ctk.CTkFont(size=24))
        product_icon.pack(pady=(15, 5))
        
        product_name = ctk.CTkLabel(
            header_frame,
            text=self.product['name'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0d47a1", "white")
        )
        product_name.pack(pady=(0, 5))
        
        product_sku = ctk.CTkLabel(
            header_frame,
            text=f"SKU: {self.product['sku']}",
            font=ctk.CTkFont(size=14),
            text_color=("#1976d2", "#e3f2fd")
        )
        product_sku.pack(pady=(0, 15))
        
        # Input fields - use scrollable frame to ensure all content is visible
        fields_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        fields_frame.pack(fill="both", expand=True, padx=15)
        
        # Quantity field
        qty_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        qty_frame.pack(fill="x", pady=(0, 15))
        
        qty_label = ctk.CTkLabel(
            qty_frame,
            text="📊 Quantity to Order:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        qty_label.pack(pady=(15, 10))
        
        self.quantity_entry = ctk.CTkEntry(
            qty_frame,
            placeholder_text="Enter quantity...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.quantity_entry.pack(padx=20, pady=(0, 15), fill="x")
        
        # Unit cost field
        cost_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        cost_frame.pack(fill="x", pady=(0, 15))
        
        cost_label = ctk.CTkLabel(
            cost_frame,
            text="💰 Unit Cost (Rs):",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        cost_label.pack(pady=(15, 10))
        
        default_cost = self.product['cost_price'] if self.product['cost_price'] else 0
        self.cost_entry = ctk.CTkEntry(
            cost_frame,
            placeholder_text="Enter unit cost...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.cost_entry.pack(padx=20, pady=(0, 5), fill="x")
        # Insert default cost if available
        if default_cost > 0:
            self.cost_entry.insert(0, str(default_cost))
        else:
            self.cost_entry.insert(0, "0.00")
        
        # Current cost display
        current_cost_label = ctk.CTkLabel(
            cost_frame,
            text=f"Current Cost: Rs{default_cost:.2f}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        current_cost_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.cancel,
            width=120,
            height=45,
            corner_radius=10,
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#e53935", "#c62828"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add to Order",
            command=self.add_product,
            width=140,
            height=45,
            corner_radius=10,
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="right")
        
        # Focus on quantity entry
        self.quantity_entry.focus()
    
    def add_product(self):
        """Add product with validation"""
        try:
            # Validate quantity
            quantity_str = self.quantity_entry.get().strip()
            if not quantity_str:
                messagebox.showerror("Error", "Please enter a quantity.")
                return
            
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return
            
            # Validate unit cost
            cost_str = self.cost_entry.get().strip()
            if not cost_str:
                messagebox.showerror("Error", "Please enter a unit cost.")
                return
            
            unit_cost = float(cost_str)
            if unit_cost < 0:
                messagebox.showerror("Error", "Unit cost cannot be negative.")
                return
            
            # Set result and close
            self.result = {
                'quantity': quantity,
                'unit_cost': unit_cost
            }
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and cost.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()
