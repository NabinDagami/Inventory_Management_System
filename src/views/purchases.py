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
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.new_purchase_btn = ctk.CTkButton(
            tab_frame,
            text="🛒 New Purchase",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("new_purchase")
        )
        self.new_purchase_btn.pack(side="left", padx=(0, 15))
        
        self.purchase_history_btn = ctk.CTkButton(
            tab_frame,
            text="📋 Purchase History",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("purchase_history")
        )
        self.purchase_history_btn.pack(side="left")
        
        # Current tab tracking
        self.current_tab = "new_purchase"
        
        # Content container — scrollable to prevent clipping of the PO section
        self.content_container = ctk.CTkScrollableFrame(main_frame)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create both interfaces
        self.create_new_purchase_interface()
        self.create_purchase_history_interface()
        
        # Show new purchase interface by default
        self.switch_tab("new_purchase")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        # Close any floating overrideredirect Toplevel popups
        try:
            root = self.parent.winfo_toplevel()
            for w in root.winfo_children():
                if isinstance(w, tk.Toplevel) and w.winfo_exists():
                    try:
                        if w.overrideredirect():
                            w.destroy()
                    except Exception:
                        pass
        except Exception:
            pass
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
        self.new_purchase_frame = ctk.CTkFrame(self.content_container)
        
        # Supplier selection header
        header_frame = ctk.CTkFrame(self.new_purchase_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        supplier_label = ctk.CTkLabel(header_frame, text="Supplier:", font=ctk.CTkFont(size=14, weight="bold"))
        supplier_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.supplier_var = tk.StringVar(value="Select Supplier...")
        self.supplier_dropdown = ctk.CTkOptionMenu(
            header_frame, 
            variable=self.supplier_var,
            command=self.on_supplier_selected,
            width=220
        )
        self.supplier_dropdown.pack(side="left", padx=5, pady=10)
        
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
        
        delivery_label = ctk.CTkLabel(header_frame, text="Expected Delivery:", font=ctk.CTkFont(size=14, weight="bold"))
        delivery_label.pack(side="left", padx=(20, 5), pady=10)
        
        self.delivery_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="YYYY-MM-DD",
            width=140
        )
        self.delivery_entry.pack(side="left", padx=5, pady=10)
        
        # Content area - single column layout (embedded PO inside product_frame)
        content_frame = ctk.CTkFrame(self.new_purchase_frame)
        content_frame.pack(fill="x", padx=10, pady=(6, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Product selection with embedded purchase order section
        self.create_product_selection(content_frame)
    
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
        """Create product selection area with product table + sales-style cart."""
        product_frame = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"), corner_radius=6)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        product_frame.grid_columnconfigure(0, weight=1)
        self.product_frame = product_frame

        # Row 0: Title
        ctk.CTkLabel(
            product_frame, text="📦 Select Products",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 6))

        # Row 1: Search entry
        search_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=(4, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        self.search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="Search products...",
            height=32
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))

        # Row 2: Products table — fixed height
        products_container = ctk.CTkFrame(product_frame, fg_color="transparent")
        products_container.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 4))
        products_container.grid_columnconfigure(0, weight=1)

        columns = ("SKU", "Name", "Current Stock", "Reorder Level", "Cost Price")
        self.products_tree = ttk.Treeview(products_container, columns=columns, show="headings", height=6)

        table_styles.apply_purchase_products_style(self.products_tree)

        column_widths = {"SKU": 120, "Name": 200, "Current Stock": 100, "Reorder Level": 100, "Cost Price": 100}
        for col in columns:
            self.products_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.products_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col != "Name" else "w", minwidth=70)

        v_scrollbar = ttk.Scrollbar(products_container, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set)

        self.products_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # Row 3: Action buttons
        button_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 4))

        add_one_button = ctk.CTkButton(
            button_frame,
            text="➕ Add 1 to PO",
            command=lambda: self.add_to_purchase_order(1),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            width=130,
            corner_radius=6,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        add_one_button.pack(side="left", padx=(0, 6))

        add_custom_button = ctk.CTkButton(
            button_frame,
            text="📝 Add Custom Qty",
            command=self.add_custom_quantity_po,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            width=140,
            corner_radius=6,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        add_custom_button.pack(side="left")

        self.products_tree.bind("<Double-1>", lambda e: self.add_to_purchase_order(1))

        # Row 4: Purchase order cart (sales-style, compact)
        self._build_purchase_order_in_product(product_frame)

    def _build_purchase_order_in_product(self, parent):
        """Build the purchase-order cart (sales-style item rows, compact)."""
        cart_outer = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"),
                                   border_width=1, border_color=("#CBD5E1", "#334155"),
                                   corner_radius=6)
        cart_outer.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 6))

        # ── Header ─────────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(cart_outer, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(6, 2))
        ctk.CTkLabel(header_frame, text="📋 Purchase Order Items",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.po_badge = ctk.CTkLabel(
            header_frame, text="(0)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white", fg_color="#3b82f6",
            corner_radius=8, padx=8, pady=2
        )
        self.po_badge.pack(side="left", padx=(8, 0))

        # ── Scrollable items area (max 200px, scrollbar when overflow) ──
        po_scroll = ctk.CTkScrollableFrame(cart_outer, fg_color="transparent", height=200)
        po_scroll.pack(fill="x", padx=6, pady=(2, 4))

        # Column headers (packed FIRST so they stay at top)
        po_header = ctk.CTkFrame(po_scroll, fg_color=("#F1F5F9", "#0F172A"), height=26)
        po_header.pack(fill="x", padx=0, pady=(0, 2))
        po_header.pack_propagate(False)
        ctk.CTkLabel(po_header, text="Product", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(po_header, text="Qty", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="left", padx=(50, 0))
        ctk.CTkLabel(po_header, text="Unit Cost", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="right", padx=(0, 60))
        ctk.CTkLabel(po_header, text="Total", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="right", padx=(0, 8))

        # Items container (packed SECOND, below header)
        self.po_items_container = ctk.CTkFrame(po_scroll, fg_color=("#FFFFFF", "#1E1E2E"))
        self.po_items_container.pack(fill="x", padx=0, pady=0)

        # ── Bottom bar: Clear Cart (left) | Subtotal / Total (right) ──
        bottom_bar = ctk.CTkFrame(cart_outer, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(2, 4))

        ctk.CTkButton(
            bottom_bar, text="🗑 Clear Cart",
            command=self.clear_purchase_order, width=85, height=24,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=("#E2E8F0", "#334155"),
            text_color=("#475569", "#94A3B8"),
            hover_color=("#CBD5E1", "#475569")
        ).pack(side="left")

        self.total_value = ctk.CTkLabel(bottom_bar, text="Rs 0.00",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color="#10b981", anchor="e")
        self.total_value.pack(side="right", padx=(0, 2))

        self.subtotal_value = ctk.CTkLabel(bottom_bar, text="Subtotal: Rs0.00",
                                            font=ctk.CTkFont(size=11))
        self.subtotal_value.pack(side="right", padx=(0, 4))

        # ── Create PO button (full-width, green when enabled) ──────────
        self.create_po_btn = ctk.CTkButton(
            cart_outer,
            text="📋 Create Purchase Order",
            command=self.create_purchase_order,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            state="disabled",
            fg_color="#374151",
            text_color="#9CA3AF",
            hover_color="#374151"
        )
        self.create_po_btn.pack(fill="x", padx=10, pady=(0, 8))

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
            self.all_products = products
            
            # Populate products tree
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            for product in products:
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
            
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def filter_products(self, *args):
        """Filter products tree based on search term."""
        search_term = self.search_var.get().lower()
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        for product in self.all_products:
            if search_term in product['name'].lower() or search_term in product['sku'].lower():
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
    
    def add_to_purchase_order(self, quantity=1, product=None, unit_cost=None):
        """Add a product to the purchase order.
        If product is None, uses the currently selected row in the products tree.
        """
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier first.")
            return

        # Resolve product from tree selection if not provided directly
        if product is None:
            selection = self.products_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a product from the list above.")
                return
            item_values = self.products_tree.item(selection[0], 'values')
            sku = item_values[0]
            for p in self.all_products:
                if p['sku'] == sku:
                    product = p
                    break
            if not product:
                messagebox.showerror("Error", "Product not found.")
                return

        if unit_cost is None:
            unit_cost = product.get('cost_price', 0) or 0.0

        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return

        # Check if product already in purchase order
        for item in self.purchase_items:
            if item['product_id'] == product['product_id']:
                item['quantity'] += quantity
                item['unit_cost'] = unit_cost
                self.update_purchase_order_display()
                return

        # New item
        self.purchase_items.append({
            'product_id': product['product_id'],
            'sku': product['sku'],
            'name': product['name'],
            'quantity': quantity,
            'unit_cost': unit_cost
        })
        self.update_purchase_order_display()

    def add_custom_quantity_po(self):
        """Add product to purchase order with custom quantity and cost."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first.")
            return
        item_values = self.products_tree.item(selection[0], 'values')
        sku = item_values[0]
        product = None
        for p in self.all_products:
            if p['sku'] == sku:
                product = p
                break
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        qty_str = tk.simpledialog.askstring("Quantity", f"Enter quantity for {product['name']}")
        if not qty_str:
            return
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return

        default_cost = product.get('cost_price', 0) or 0.0
        cost_str = tk.simpledialog.askstring(
            "Unit Cost",
            f"Enter unit cost for {product['name']}\n(Current cost: Rs{default_cost:.2f})",
            initialvalue=str(default_cost)
        )
        if not cost_str:
            return
        try:
            unit_cost = float(cost_str)
            if unit_cost < 0:
                messagebox.showerror("Error", "Unit cost cannot be negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid cost")
            return

        self.add_to_purchase_order(quantity, product, unit_cost)
    
    # ── Inline item helpers (sales-style) ─────────────────────────────

    def _inc_po_item(self, index):
        """Increment quantity of PO item at index."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items[index]['quantity'] += 1
            self.update_purchase_order_display()

    def _dec_po_item(self, index):
        """Decrement quantity of PO item at index. Removes item if qty reaches 0."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items[index]['quantity'] -= 1
            if self.purchase_items[index]['quantity'] <= 0:
                self.purchase_items.pop(index)
            self.update_purchase_order_display()

    def _remove_po_item(self, index):
        """Remove PO item at index."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items.pop(index)
            self.update_purchase_order_display()
    
    def clear_purchase_order(self):
        """Clear all items from purchase order"""
        if self.purchase_items:
            if messagebox.askyesno("Confirm", "Clear all items from purchase order?"):
                self.purchase_items = []
                self.update_purchase_order_display()
    
    def update_purchase_order_display(self):
        """Update cart display with inline controls and totals (sales-style)."""
        # Clear inline items
        for w in self.po_items_container.winfo_children():
            w.destroy()

        subtotal = 0

        for idx, item in enumerate(self.purchase_items):
            total_cost = item['unit_cost'] * item['quantity']
            subtotal += total_cost

            bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
            is_dark = ctk.get_appearance_mode() == "Dark"
            if is_dark:
                bg = "#1E1E2E" if idx % 2 == 0 else "#1A1A2E"

            row_frame = ctk.CTkFrame(self.po_items_container, fg_color=bg, height=34)
            row_frame.pack(fill="x", padx=1, pady=(0, 1))
            row_frame.pack_propagate(False)

            # Product name
            name = item['name'][:18] + ".." if len(item['name']) > 18 else item['name']
            ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=10),
                         anchor="w").pack(side="left", padx=(8, 0), expand=True, fill="x")

            # [-] button
            dec_btn = ctk.CTkButton(
                row_frame, text="−", width=26, height=24,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("#FF6B35", "#D35400"), hover_color=("#E55A2B", "#B64900"),
                command=lambda i=idx: self._dec_po_item(i)
            )
            dec_btn.pack(side="left", padx=(2, 1))
            if item['quantity'] <= 1:
                dec_btn.configure(state="disabled")

            # Qty label
            ctk.CTkLabel(row_frame, text=str(item['quantity']),
                          font=ctk.CTkFont(size=11, weight="bold"), width=22).pack(side="left", padx=(1, 1))

            # [+] button
            inc_btn = ctk.CTkButton(
                row_frame, text="+", width=26, height=24,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("#2196F3", "#1565C0"), hover_color=("#1976D2", "#0D47A1"),
                command=lambda i=idx: self._inc_po_item(i)
            )
            inc_btn.pack(side="left", padx=(1, 4))

            # Unit cost — editable entry
            cost_var = tk.StringVar(value=f"{item['unit_cost']:.2f}")
            cost_entry = ctk.CTkEntry(
                row_frame, textvariable=cost_var, width=80, height=24,
                font=ctk.CTkFont(size=10),
                justify="right",
                border_width=1,
                fg_color=("#FFFFFF", "#1E1E2E"),
                text_color=("#64748B", "#94A3B8")
            )
            cost_entry.pack(side="right", padx=(0, 4))
            def on_cost_change(e, i=idx, var=cost_var):
                try:
                    new_cost = float(var.get())
                    if new_cost >= 0:
                        self.purchase_items[i]['unit_cost'] = new_cost
                        self.update_purchase_order_display()
                except ValueError:
                    pass
            cost_entry.bind("<FocusOut>", on_cost_change)
            cost_entry.bind("<Return>", on_cost_change)

            # Total label
            ctk.CTkLabel(row_frame, text=f"Rs{total_cost:.2f}",
                         font=ctk.CTkFont(size=10, weight="bold")).pack(side="right", padx=(0, 4))

            # [×] remove button
            remove_btn = ctk.CTkButton(
                row_frame, text="×", width=24, height=22,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#FEE2E2", "#3B0A0A"), hover_color=("#FECACA", "#5B1A1A"),
                text_color=("#DC2626", "#FCA5A5"),
                command=lambda i=idx: self._remove_po_item(i)
            )
            remove_btn.pack(side="right", padx=(2, 4))

        # Update summary
        self.subtotal_value.configure(text=f"Subtotal: Rs{subtotal:.2f}")
        self.total_value.configure(text=f"Rs {subtotal:,.2f}")

        # Update badge
        count = len(self.purchase_items)
        self.po_badge.configure(text=f"({count})")

        # Enable/disable create button
        if count > 0:
            self.create_po_btn.configure(
                text=f"📋 Create Purchase Order — Rs {subtotal:,.2f}",
                state="normal",
                fg_color="#10B981",
                text_color="#FFFFFF",
                hover_color="#059669"
            )
        else:
            self.create_po_btn.configure(
                text="📋 Create Purchase Order",
                state="disabled",
                fg_color="#374151",
                text_color="#9CA3AF",
                hover_color="#374151"
            )
    
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
        """Mark selected purchase order as received and update stock"""
        selected = self.purchase_history_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase order first.")
            return

        values = self.purchase_history_tree.item(selected[0], "values")
        po_number = values[0]

        # Look up purchase_id from stored data
        purchase_id = None
        for p in self.all_purchase_data:
            if p['po_number'] == po_number:
                purchase_id = p['purchase_id']
                break

        if not purchase_id:
            messagebox.showerror("Error", "Could not find purchase order data.")
            return

        confirm = messagebox.askyesno("Confirm", f"Mark {po_number} as received?\n\nThis will update product stock levels.")
        if not confirm:
            return

        try:
            # Get purchase items
            items = db.execute_query("""
                SELECT product_id, quantity FROM purchase_items WHERE purchase_id = ?
            """, (purchase_id,))

            # Update stock for each item
            for item in items:
                db.execute_update("""
                    UPDATE products SET stock = stock + ? WHERE product_id = ?
                """, (item['quantity'], item['product_id']))

            # Update purchase status
            db.execute_update("""
                UPDATE purchases SET status = 'received' WHERE id = ?
            """, (purchase_id,))

            messagebox.showinfo("Success", f"{po_number} marked as received.\nStock levels updated.")
            self.load_purchase_history()

        except Exception as e:
            print(f"Error marking as received: {e}")
            messagebox.showerror("Error", f"Failed to mark as received: {e}")
    
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
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 500
        dialog_height = 500
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
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
