import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from utils.sku_generator import SKUGenerator
import utils.simple_table_styles as table_styles
from utils.export_manager import ExportManager

class InventoryView:
    def __init__(self, parent):
        self.parent = parent
        self.current_tab = "products"
        self.create_inventory_view()
        self.load_data()
    
    def create_inventory_view(self):
        """Create inventory management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with tabs and action buttons
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame)
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.products_btn = ctk.CTkButton(
            tab_frame,
            text="Products",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("products")
        )
        self.products_btn.pack(side="left", padx=(0, 10))
        
        self.categories_btn = ctk.CTkButton(
            tab_frame,
            text="Categories",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("categories")
        )
        self.categories_btn.pack(side="left", padx=(0, 10))
        
        self.sub_categories_btn = ctk.CTkButton(
            tab_frame,
            text="Sub Categories",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("sub_categories")
        )
        self.sub_categories_btn.pack(side="left", padx=(0, 10))
        
        self.brands_btn = ctk.CTkButton(
            tab_frame,
            text="Brands",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("brands")
        )
        self.brands_btn.pack(side="left", padx=(0, 10))
        
        self.sub_brands_btn = ctk.CTkButton(
            tab_frame,
            text="Sub Brands",
            width=110,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("sub_brands")
        )
        self.sub_brands_btn.pack(side="left")
        
        # Action buttons - Visual Hierarchy
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=10)
        
        # Primary Action: Add Product (Blue)
        self.add_btn = ctk.CTkButton(
            action_frame,
            text="Add Product",
            width=130,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.add_item,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=8
        )
        self.add_btn.pack(side="left", padx=(0, 8))
        
        # Secondary: Edit (Outline)
        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="Edit",
            width=80,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.edit_item,
            fg_color="transparent",
            border_color="#6B7280",
            border_width=2,
            text_color=("gray10", "gray90"),
            hover_color=("gray85", "gray25"),
            corner_radius=8
        )
        self.edit_btn.pack(side="left", padx=(0, 8))
        
        # Danger: Delete (Red)
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="Delete",
            width=90,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.delete_item,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=8
        )
        self.delete_btn.pack(side="left", padx=(0, 15))
        
        # Export Dropdown
        self.export_menu = ctk.CTkOptionMenu(
            action_frame,
            values=["Export", "Excel", "PDF"],
            width=110,
            height=38,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.handle_export,
            fg_color="#6B7280",
            button_color="#4B5563",
            button_hover_color="#374151",
            corner_radius=8
        )
        self.export_menu.pack(side="left")
        self.export_menu.set("Export")
        
        # Search and Filter frame
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Row 1: Search box
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=10, pady=(10, 5))
        
        search_label = ctk.CTkLabel(search_row, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        search_entry = ctk.CTkEntry(
            search_row,
            textvariable=self.search_var,
            placeholder_text="Search by name or SKU...",
            width=300
        )
        search_entry.pack(side="left", padx=5)
        
        # Row 2: Advanced filters - inline layout
        filters_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filters_row.pack(fill="x", padx=10, pady=(5, 10))
        
        # Category filter
        cat_label = ctk.CTkLabel(filters_row, text="Category:", font=ctk.CTkFont(size=11, weight="bold"))
        cat_label.pack(side="left", padx=(0, 5))
        
        self.category_filter_var = tk.StringVar(value="All")
        self.category_filter = ctk.CTkOptionMenu(
            filters_row,
            variable=self.category_filter_var,
            values=["All"],
            width=140,
            command=lambda x: self.filter_data()
        )
        self.category_filter.pack(side="left", padx=(0, 12))
        
        # Sub Category filter
        sub_cat_label = ctk.CTkLabel(filters_row, text="Sub Category:", font=ctk.CTkFont(size=11, weight="bold"))
        sub_cat_label.pack(side="left", padx=(0, 5))
        
        self.sub_category_filter_var = tk.StringVar(value="All")
        self.sub_category_filter = ctk.CTkOptionMenu(
            filters_row,
            variable=self.sub_category_filter_var,
            values=["All"],
            width=140,
            command=lambda x: self.filter_data()
        )
        self.sub_category_filter.pack(side="left", padx=(0, 12))
        
        # Brand filter
        brand_label = ctk.CTkLabel(filters_row, text="Brand:", font=ctk.CTkFont(size=11, weight="bold"))
        brand_label.pack(side="left", padx=(0, 5))
        
        self.brand_filter_var = tk.StringVar(value="All")
        self.brand_filter = ctk.CTkOptionMenu(
            filters_row,
            variable=self.brand_filter_var,
            values=["All"],
            width=140,
            command=lambda x: self.filter_data()
        )
        self.brand_filter.pack(side="left", padx=(0, 12))
        
        # Sub Brand filter
        sub_brand_label = ctk.CTkLabel(filters_row, text="Sub Brand:", font=ctk.CTkFont(size=11, weight="bold"))
        sub_brand_label.pack(side="left", padx=(0, 5))
        
        self.sub_brand_filter_var = tk.StringVar(value="All")
        self.sub_brand_filter = ctk.CTkOptionMenu(
            filters_row,
            variable=self.sub_brand_filter_var,
            values=["All"],
            width=140,
            command=lambda x: self.filter_data()
        )
        self.sub_brand_filter.pack(side="left", padx=(0, 12))
        
        # Stock status filter
        stock_label = ctk.CTkLabel(filters_row, text="Stock:", font=ctk.CTkFont(size=11, weight="bold"))
        stock_label.pack(side="left", padx=(0, 5))
        
        self.stock_filter_var = tk.StringVar(value="All")
        self.stock_filter = ctk.CTkOptionMenu(
            filters_row,
            variable=self.stock_filter_var,
            values=["All", "In Stock", "Low Stock", "Out of Stock"],
            width=120,
            command=lambda x: self.filter_data()
        )
        self.stock_filter.pack(side="left", padx=(0, 12))
        
        # Clear filters button - inline with filters
        clear_btn = ctk.CTkButton(
            filters_row,
            text="Clear",
            command=self.clear_filters,
            width=90,
            height=28,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=11)
        )
        clear_btn.pack(side="left")
        
        # Summary cards row
        self.create_summary_cards(main_frame)
        
        # Content area with table
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create table
        self.create_table(content_frame)
    
    def create_summary_cards(self, parent):
        """Create compact summary cards showing inventory statistics"""
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        # Card 1: Total Products (compact)
        self.total_card = ctk.CTkFrame(cards_frame, corner_radius=8, fg_color="#3B82F6", cursor="hand2", height=60)
        self.total_card.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.total_card.pack_propagate(False)
        self.total_card.bind("<Button-1>", lambda e: self.show_all_products())
        ctk.CTkLabel(self.total_card, text="Total", font=ctk.CTkFont(size=10), text_color="white").pack(pady=(5, 0))
        self.total_label = ctk.CTkLabel(self.total_card, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.total_label.pack(pady=(0, 5))
        
        # Card 2: Low Stock (compact)
        self.low_stock_card = ctk.CTkFrame(cards_frame, corner_radius=8, fg_color="#D97706", cursor="hand2", height=60)
        self.low_stock_card.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.low_stock_card.pack_propagate(False)
        self.low_stock_card.bind("<Button-1>", lambda e: self.filter_by_stock_status("Low Stock"))
        ctk.CTkLabel(self.low_stock_card, text="Low", font=ctk.CTkFont(size=10), text_color="white").pack(pady=(5, 0))
        self.low_stock_label = ctk.CTkLabel(self.low_stock_card, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.low_stock_label.pack(pady=(0, 5))
        
        # Card 3: Out of Stock (compact)
        self.out_stock_card = ctk.CTkFrame(cards_frame, corner_radius=8, fg_color="#DC2626", cursor="hand2", height=60)
        self.out_stock_card.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.out_stock_card.pack_propagate(False)
        self.out_stock_card.bind("<Button-1>", lambda e: self.filter_by_stock_status("Out of Stock"))
        ctk.CTkLabel(self.out_stock_card, text="Out", font=ctk.CTkFont(size=10), text_color="white").pack(pady=(5, 0))
        self.out_stock_label = ctk.CTkLabel(self.out_stock_card, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.out_stock_label.pack(pady=(0, 5))
        
        # Card 4: Inventory Value (compact)
        self.value_card = ctk.CTkFrame(cards_frame, corner_radius=8, fg_color="#059669", height=60)
        self.value_card.pack(side="left", fill="x", expand=True)
        self.value_card.pack_propagate(False)
        ctk.CTkLabel(self.value_card, text="Value", font=ctk.CTkFont(size=10), text_color="white").pack(pady=(5, 0))
        self.value_label = ctk.CTkLabel(self.value_card, text="Rs 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.value_label.pack(pady=(0, 5))
    
    def show_all_products(self):
        """Show all products by clearing filters"""
        self.clear_filters()
    
    def filter_by_stock_status(self, status):
        """Filter table by stock status"""
        self.stock_filter_var.set(status)
        self.filter_data()
    
    def _cleanup_scrollbars(self):
        """Clean up scrollbar references before destroying treeview to prevent TclError"""
        try:
            # Reset scrollbar commands to prevent calls to destroyed widgets
            if hasattr(self, 'h_scrollbar') and self.h_scrollbar and self.h_scrollbar.winfo_exists():
                self.h_scrollbar.configure(command=None)
            if hasattr(self, 'v_scrollbar') and self.v_scrollbar and self.v_scrollbar.winfo_exists():
                self.v_scrollbar.configure(command=None)
            # Reset treeview scroll commands
            if hasattr(self, 'data_tree') and self.data_tree and self.data_tree.winfo_exists():
                self.data_tree.configure(yscrollcommand=None, xscrollcommand=None)
        except Exception:
            # Ignore any errors during cleanup
            pass
    
    def create_table(self, parent):
        """Create the data table"""
        # Table frame
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Products table (default)
        self.create_products_table(table_frame)
    
    def create_products_table(self, parent):
        """Create products table with enhanced styling and smooth animations"""
        # Clear existing table - first unconfigure scrollbars to prevent errors
        self._cleanup_scrollbars()
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create treeview frame with border
        table_container = ctk.CTkFrame(parent, border_width=2, border_color=("gray70", "gray30"))
        table_container.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for products
        columns = ("SKU", "Name", "Category", "Sub Category", "Brand", "Sub Brand", "Stock", "Normal Price", "Workshop Price", "Reorder Level")
        self.data_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=20)
        
        # Apply centralized styling
        table_styles.apply_product_style(self.data_tree)
        
        # Configure tags for row styling
        self.data_tree.tag_configure("evenrow", background="#E5E7EB")
        self.data_tree.tag_configure("oddrow", background="#F3F4F6")
        self.data_tree.tag_configure("hover", background="#D1D5DB")  # Hover effect
        # Stock status colors - only for stock column
        self.data_tree.tag_configure("stock_zero", foreground="#DC2626", font=("Segoe UI", 11, "bold"))
        self.data_tree.tag_configure("stock_low", foreground="#D97706", font=("Segoe UI", 11, "bold"))
        self.data_tree.tag_configure("stock_ok", foreground="#059669", font=("Segoe UI", 11))
        
        # Define headings and column widths - wider for better visibility
        column_widths = {"SKU": 100, "Name": 200, "Category": 120, "Sub Category": 120, 
                        "Brand": 120, "Sub Brand": 120, "Stock": 80, 
                        "Normal Price": 100, "Workshop Price": 120, "Reorder Level": 100}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 100), anchor="center", minwidth=80)
        
        # Scrollbars with modern styling
        self.v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.data_tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Pack table and scrollbars
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        self.v_scrollbar.pack(side="right", fill="y", pady=2)
        self.h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        # Bind double-click to edit
        self.data_tree.bind("<Double-1>", lambda e: self.edit_item())
        
        # Add hover effect binding
        self.data_tree.bind("<Motion>", self.on_table_hover)
        
        # Bind right-click for context menu
        self.data_tree.bind("<Button-3>", self.show_context_menu)
        
        # Create styled context menu matching dark theme
        self.context_menu = tk.Menu(self.parent, tearoff=0, bg="#2D2D2D", fg="#FFFFFF", 
                                    activebackground="#3B82F6", activeforeground="#FFFFFF",
                                    borderwidth=0, font=("Segoe UI", 11))
        self.context_menu.add_command(label="  Edit", command=self.edit_item)
        self.context_menu.add_command(label="  Quick Stock +1", command=lambda: self.quick_stock_adjust(1))
        self.context_menu.add_command(label="  Quick Stock -1", command=lambda: self.quick_stock_adjust(-1))
        self.context_menu.add_separator(background="#404040")
        self.context_menu.add_command(label="  Delete", command=self.delete_item, foreground="#EF4444")
        
        # Item count label below table
        self.count_label = ctk.CTkLabel(parent, text="Showing 0 of 0 items", font=ctk.CTkFont(size=11), text_color="gray")
        self.count_label.pack(side="bottom", anchor="w", padx=5, pady=(5, 0))
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select row under mouse
        row_id = self.data_tree.identify_row(event.y)
        if row_id:
            self.data_tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)
    
    def quick_stock_adjust(self, amount):
        """Quickly adjust stock by +/- 1"""
        selection = self.data_tree.selection()
        if not selection:
            return
        
        item_values = self.data_tree.item(selection[0], 'values')
        sku = item_values[0]
        
        # Get current stock
        product = db.execute_query("SELECT stock FROM products WHERE sku = ?", (sku,))
        if not product:
            return
        
        current_stock = product[0]['stock']
        new_stock = current_stock + amount
        
        # Validate - prevent negative stock
        if new_stock < 0:
            messagebox.showerror("Invalid Operation", "Stock cannot be negative!")
            return
        
        # Update stock
        try:
            db.execute_update("UPDATE products SET stock = ? WHERE sku = ?", (new_stock, sku))
            self.load_data()
            messagebox.showinfo("Success", f"Stock updated! New stock: {new_stock}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {e}")
    
    def create_categories_table(self, parent):
        """Create categories table with enhanced styling"""
        # Clear existing table - first unconfigure scrollbars to prevent errors
        self._cleanup_scrollbars()
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create treeview for categories
        columns = ("ID", "Name", "Description", "Created")
        self.data_tree = ttk.Treeview(parent, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_category_style(self.data_tree)
        
        # Define headings and column widths
        column_widths = {"ID": 80, "Name": 250, "Description": 450, "Created": 180}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col == "ID" else "w", minwidth=80)
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.v_scrollbar.pack(side="right", fill="y", pady=5)
        self.h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        self.data_tree.bind("<Double-1>", lambda e: self.edit_item())
    
    def create_sub_categories_table(self, parent):
        """Create sub categories table with enhanced styling"""
        # Clear existing table - first unconfigure scrollbars to prevent errors
        self._cleanup_scrollbars()
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create treeview for sub categories
        columns = ("ID", "Name", "Category", "Description", "Created")
        self.data_tree = ttk.Treeview(parent, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_category_style(self.data_tree)
        
        # Define headings and column widths
        column_widths = {"ID": 80, "Name": 200, "Category": 150, "Description": 350, "Created": 180}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col == "ID" else "w", minwidth=80)
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.v_scrollbar.pack(side="right", fill="y", pady=5)
        self.h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        self.data_tree.bind("<Double-1>", lambda e: self.edit_item())
    
    def create_brands_table(self, parent):
        """Create brands table with enhanced styling"""
        # Clear existing table - first unconfigure scrollbars to prevent errors
        self._cleanup_scrollbars()
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create treeview for brands
        columns = ("ID", "Name", "Description", "Created")
        self.data_tree = ttk.Treeview(parent, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_brand_style(self.data_tree)
        
        # Define headings and column widths
        column_widths = {"ID": 80, "Name": 250, "Description": 450, "Created": 180}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col == "ID" else "w", minwidth=80)
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.v_scrollbar.pack(side="right", fill="y", pady=5)
        self.h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        self.data_tree.bind("<Double-1>", lambda e: self.edit_item())
    
    def create_sub_brands_table(self, parent):
        """Create sub brands table with enhanced styling"""
        # Clear existing table - first unconfigure scrollbars to prevent errors
        self._cleanup_scrollbars()
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create treeview for sub brands
        columns = ("ID", "Name", "Brand", "Description", "Created")
        self.data_tree = ttk.Treeview(parent, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_brand_style(self.data_tree)
        
        # Define headings and column widths
        column_widths = {"ID": 80, "Name": 200, "Brand": 150, "Description": 350, "Created": 180}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col == "ID" else "w", minwidth=80)
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.data_tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.v_scrollbar.pack(side="right", fill="y", pady=5)
        self.h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        self.data_tree.bind("<Double-1>", lambda e: self.edit_item())
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab = tab_name
        
        # Update button styles
        active_color = ("#1f538d", "#14375e")
        inactive_color = ("gray85", "gray25")
        inactive_text_color = ("gray10", "gray90")
        
        # Reset all buttons to inactive
        self.products_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        self.categories_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        self.sub_categories_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        self.brands_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        self.sub_brands_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        
        # Set active button
        if tab_name == "products":
            self.products_btn.configure(fg_color=active_color, text_color="white")
        elif tab_name == "categories":
            self.categories_btn.configure(fg_color=active_color, text_color="white")
        elif tab_name == "sub_categories":
            self.sub_categories_btn.configure(fg_color=active_color, text_color="white")
        elif tab_name == "brands":
            self.brands_btn.configure(fg_color=active_color, text_color="white")
        elif tab_name == "sub_brands":
            self.sub_brands_btn.configure(fg_color=active_color, text_color="white")
        
        # Update add button text
        button_texts = {
            "products": "Add Product",
            "categories": "Add Category",
            "sub_categories": "Add Sub Category",
            "brands": "Add Brand",
            "sub_brands": "Add Sub Brand"
        }
        self.add_btn.configure(text=button_texts.get(tab_name, "Add"))
        
        # Show/hide filter frame based on tab
        filter_frame = self.search_var.trace_info()
        
        # Recreate table for current tab
        content_frame = self.data_tree.master
        if tab_name == "products":
            self.create_products_table(content_frame)
        elif tab_name == "categories":
            self.create_categories_table(content_frame)
        elif tab_name == "sub_categories":
            self.create_sub_categories_table(content_frame)
        elif tab_name == "brands":
            self.create_brands_table(content_frame)
        elif tab_name == "sub_brands":
            self.create_sub_brands_table(content_frame)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load data for current tab"""
        try:
            # Clear existing items
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            if self.current_tab == "products":
                self.load_products_data()
            elif self.current_tab == "categories":
                self.load_categories_data()
            elif self.current_tab == "sub_categories":
                self.load_sub_categories_data()
            elif self.current_tab == "brands":
                self.load_brands_data()
            elif self.current_tab == "sub_brands":
                self.load_sub_brands_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def on_table_hover(self, event):
        """Handle mouse hover over table rows for visual feedback"""
        row_id = self.data_tree.identify_row(event.y)
        if row_id:
            self.data_tree.config(cursor="hand2")
        else:
            self.data_tree.config(cursor="")

    def format_price(self, price):
        """Format price with comma separators"""
        return f"Rs {price:,.0f}"
    
    def get_stock_status_tag(self, stock, reorder_level):
        """Get stock status color tag - only for stock column"""
        if stock == 0:
            return "stock_zero"  # Red
        elif stock <= reorder_level:
            return "stock_low"   # Orange/Yellow
        else:
            return "stock_ok"    # Green
    
    def load_products_data(self):
        """Load products data with proper formatting, stock colors, and summary stats"""
        query = """
            SELECT p.sku, p.name, c.category_name, sc.sub_category_name, 
                   b.brand_name, sb.sub_brand_name, p.stock, 
                   p.price_normal, p.price_workshop, p.reorder_level, p.cost_price
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN sub_categories sc ON p.sub_category_id = sc.sub_category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN sub_brands sb ON p.sub_brand_id = sb.sub_brand_id
            WHERE p.is_active = 1
            ORDER BY p.name
        """
        products = db.execute_query(query)
        
        self.all_data = products  # Store for filtering
        
        # Calculate summary statistics
        total_products = len(products)
        low_stock_count = sum(1 for p in products if 0 < p['stock'] <= p['reorder_level'])
        out_stock_count = sum(1 for p in products if p['stock'] == 0)
        inventory_value = sum(p['stock'] * p['cost_price'] for p in products)
        
        # Update summary cards
        self.total_label.configure(text=str(total_products))
        self.low_stock_label.configure(text=str(low_stock_count))
        self.out_stock_label.configure(text=str(out_stock_count))
        self.value_label.configure(text=self.format_price(inventory_value))
        
        # Load filter options
        self.load_filter_options()
        
        # Insert data with proper formatting
        for idx, product in enumerate(products):
            # Determine row tag for alternating colors only
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            
            # Stock display with status icon and label
            stock = product['stock']
            reorder = product['reorder_level']
            if stock == 0:
                stock_display = "0  Out"
            elif stock <= reorder:
                stock_display = f"{stock}  Low"
            else:
                stock_display = f"{stock}  OK"
            
            # Get stock color tag (only for stock column)
            stock_tag = self.get_stock_status_tag(stock, reorder)
            
            # Insert the item
            item_id = self.data_tree.insert("", "end", values=(
                product['sku'],
                product['name'],
                product['category_name'] or "N/A",
                product['sub_category_name'] or "N/A",
                product['brand_name'] or "N/A",
                product['sub_brand_name'] or "N/A",
                stock_display,
                self.format_price(product['price_normal']),
                self.format_price(product['price_workshop']),
                reorder
            ), tags=(row_tag,))
            
            # Apply stock color ONLY to stock column
            self.data_tree.item(item_id, tags=(row_tag, stock_tag))
        
        # Update count label if it exists
        displayed_count = len(self.data_tree.get_children())
        if hasattr(self, 'count_label'):
            self.count_label.configure(text=f"Showing {displayed_count} of {total_products} items")
    
    def load_categories_data(self):
        """Load categories data"""
        categories = db.execute_query("SELECT * FROM categories ORDER BY category_name")
        self.all_data = categories
        
        for category in categories:
            self.data_tree.insert("", "end", values=(
                category['category_id'],
                category['category_name'],
                category['description'] or "N/A",
                category['created_at']
            ))
    
    def load_sub_categories_data(self):
        """Load sub categories data"""
        query = """
            SELECT sc.*, c.category_name 
            FROM sub_categories sc
            LEFT JOIN categories c ON sc.category_id = c.category_id
            ORDER BY sc.sub_category_name
        """
        sub_categories = db.execute_query(query)
        self.all_data = sub_categories
        
        for sc in sub_categories:
            self.data_tree.insert("", "end", values=(
                sc['sub_category_id'],
                sc['sub_category_name'],
                sc['category_name'] or "N/A",
                sc['description'] or "N/A",
                sc['created_at']
            ))
    
    def load_brands_data(self):
        """Load brands data"""
        brands = db.execute_query("SELECT * FROM brands ORDER BY brand_name")
        self.all_data = brands
        
        for brand in brands:
            self.data_tree.insert("", "end", values=(
                brand['brand_id'],
                brand['brand_name'],
                brand['description'] or "N/A",
                brand['created_at']
            ))
    
    def load_sub_brands_data(self):
        """Load sub brands data"""
        query = """
            SELECT sb.*, b.brand_name 
            FROM sub_brands sb
            LEFT JOIN brands b ON sb.brand_id = b.brand_id
            ORDER BY sb.sub_brand_name
        """
        sub_brands = db.execute_query(query)
        self.all_data = sub_brands
        
        for sb in sub_brands:
            self.data_tree.insert("", "end", values=(
                sb['sub_brand_id'],
                sb['sub_brand_name'],
                sb['brand_name'] or "N/A",
                sb['description'] or "N/A",
                sb['created_at']
            ))
    
    def load_filter_options(self):
        """Load categories and brands for filter dropdowns"""
        # Load categories
        categories = db.execute_query("SELECT category_name FROM categories ORDER BY category_name")
        cat_values = ["All"] + [cat['category_name'] for cat in categories if cat['category_name']]
        self.category_filter.configure(values=cat_values)
        
        # Load sub categories
        sub_categories = db.execute_query("SELECT sub_category_name FROM sub_categories ORDER BY sub_category_name")
        sub_cat_values = ["All"] + [sc['sub_category_name'] for sc in sub_categories if sc['sub_category_name']]
        self.sub_category_filter.configure(values=sub_cat_values)
        
        # Load brands
        brands = db.execute_query("SELECT brand_name FROM brands ORDER BY brand_name")
        brand_values = ["All"] + [brand['brand_name'] for brand in brands if brand['brand_name']]
        self.brand_filter.configure(values=brand_values)
        
        # Load sub brands
        sub_brands = db.execute_query("SELECT sub_brand_name FROM sub_brands ORDER BY sub_brand_name")
        sub_brand_values = ["All"] + [sb['sub_brand_name'] for sb in sub_brands if sb['sub_brand_name']]
        self.sub_brand_filter.configure(values=sub_brand_values)
    
    def clear_filters(self):
        """Clear all filters and reload data"""
        self.search_var.set("")
        self.category_filter_var.set("All")
        self.sub_category_filter_var.set("All")
        self.brand_filter_var.set("All")
        self.sub_brand_filter_var.set("All")
        self.stock_filter_var.set("All")
        self.filter_data()
    
    def filter_data(self, *args):
        """Filter data based on search and filter criteria"""
        search_term = self.search_var.get().lower()
        selected_category = self.category_filter_var.get()
        selected_sub_category = self.sub_category_filter_var.get()
        selected_brand = self.brand_filter_var.get()
        selected_sub_brand = self.sub_brand_filter_var.get()
        selected_stock = self.stock_filter_var.get()
        
        # Clear tree
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not hasattr(self, 'all_data'):
            return
        
        # Filter and display matching items
        for item in self.all_data:
            if self.current_tab == "products":
                # Text search filter
                matches_search = (search_term in item['name'].lower() or 
                                  search_term in item['sku'].lower())
                
                # Category filter
                category_name = item['category_name'] if item['category_name'] else "N/A"
                matches_category = (selected_category == "All" or 
                                    category_name == selected_category)
                
                # Sub Category filter
                sub_category_name = item['sub_category_name'] if item['sub_category_name'] else "N/A"
                matches_sub_category = (selected_sub_category == "All" or 
                                        sub_category_name == selected_sub_category)
                
                # Brand filter
                brand_name = item['brand_name'] if item['brand_name'] else "N/A"
                matches_brand = (selected_brand == "All" or 
                                 brand_name == selected_brand)
                
                # Sub Brand filter
                sub_brand_name = item['sub_brand_name'] if item['sub_brand_name'] else "N/A"
                matches_sub_brand = (selected_sub_brand == "All" or 
                                     sub_brand_name == selected_sub_brand)
                
                # Stock status filter
                stock = item['stock']
                reorder_level = item['reorder_level']
                if selected_stock == "All":
                    matches_stock = True
                elif selected_stock == "In Stock":
                    matches_stock = stock > reorder_level
                elif selected_stock == "Low Stock":
                    matches_stock = 0 < stock <= reorder_level
                elif selected_stock == "Out of Stock":
                    matches_stock = stock == 0
                else:
                    matches_stock = True
                
                # Apply all filters
                if matches_search and matches_category and matches_sub_category and matches_brand and matches_sub_brand and matches_stock:
                    # Stock display with status icon and label
                    if stock == 0:
                        stock_display = "0  Out"
                    elif stock <= reorder_level:
                        stock_display = f"{stock}  Low"
                    else:
                        stock_display = f"{stock}  OK"
                    
                    # Get stock color tag
                    stock_tag = self.get_stock_status_tag(stock, reorder_level)
                    
                    # Insert the item
                    item_id = self.data_tree.insert("", "end", values=(
                        item['sku'],
                        item['name'],
                        category_name,
                        sub_category_name,
                        brand_name,
                        sub_brand_name,
                        stock_display,
                        self.format_price(item['price_normal']),
                        self.format_price(item['price_workshop']),
                        reorder_level
                    ), tags=(stock_tag,))
            elif self.current_tab == "categories":
                if search_term in item['category_name'].lower():
                    self.data_tree.insert("", "end", values=(
                        item['category_id'],
                        item['category_name'],
                        item['description'] or "N/A",
                        item['created_at']
                    ))
            elif self.current_tab == "sub_categories":
                if search_term in item['sub_category_name'].lower():
                    self.data_tree.insert("", "end", values=(
                        item['sub_category_id'],
                        item['sub_category_name'],
                        item['category_name'] or "N/A",
                        item['description'] or "N/A",
                        item['created_at']
                    ))
            elif self.current_tab == "brands":
                if search_term in item['brand_name'].lower():
                    self.data_tree.insert("", "end", values=(
                        item['brand_id'],
                        item['brand_name'],
                        item['description'] or "N/A",
                        item['created_at']
                    ))
            elif self.current_tab == "sub_brands":
                if search_term in item['sub_brand_name'].lower():
                    self.data_tree.insert("", "end", values=(
                        item['sub_brand_id'],
                        item['sub_brand_name'],
                        item['brand_name'] or "N/A",
                        item['description'] or "N/A",
                        item['created_at']
                    ))
        
        # Configure tag for low stock items - red color (need to do this after inserting items)
        if self.current_tab == "products":
            self.data_tree.tag_configure("low_stock", foreground="#FF0000")
    
    def add_item(self):
        """Add new item based on current tab"""
        if self.current_tab == "products":
            self.add_product()
        elif self.current_tab == "categories":
            self.add_category()
        elif self.current_tab == "sub_categories":
            self.add_sub_category()
        elif self.current_tab == "brands":
            self.add_brand()
        elif self.current_tab == "sub_brands":
            self.add_sub_brand()
    
    def add_product(self):
        """Add new product"""
        dialog = ProductDialog(self.parent, "Add Product")
        if dialog.result:
            try:
                # Generate SKU
                sku = SKUGenerator.generate_sku(dialog.result['category_id'], dialog.result['brand_id'])
                
                # Insert product
                db.execute_insert(
                    """INSERT INTO products (name, sku, category_id, sub_category_id, brand_id, sub_brand_id, description, 
                                           stock, price_normal, price_workshop, cost_price, reorder_level)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (dialog.result['name'], sku, dialog.result['category_id'], dialog.result['sub_category_id'],
                     dialog.result['brand_id'], dialog.result['sub_brand_id'],
                     dialog.result['description'], dialog.result['stock'], dialog.result['price_normal'],
                     dialog.result['price_workshop'], dialog.result['cost_price'], dialog.result['reorder_level'])
                )
                
                messagebox.showinfo("Success", f"Product added successfully!\nSKU: {sku}")
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")
    
    def add_category(self):
        """Add new category"""
        dialog = CategoryDialog(self.parent, "Add Category")
        if dialog.result:
            try:
                db.execute_insert(
                    "INSERT INTO categories (category_name, description) VALUES (?, ?)",
                    (dialog.result['name'], dialog.result['description'])
                )
                messagebox.showinfo("Success", "Category added successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add category: {e}")
    
    def add_sub_category(self):
        """Add new sub category"""
        dialog = SubCategoryDialog(self.parent, "Add Sub Category")
        if dialog.result:
            try:
                db.execute_insert(
                    "INSERT INTO sub_categories (sub_category_name, category_id, description) VALUES (?, ?, ?)",
                    (dialog.result['name'], dialog.result['category_id'], dialog.result['description'])
                )
                messagebox.showinfo("Success", "Sub Category added successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sub category: {e}")
    
    def add_brand(self):
        """Add new brand"""
        dialog = BrandDialog(self.parent, "Add Brand")
        if dialog.result:
            try:
                db.execute_insert(
                    "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
                    (dialog.result['name'], dialog.result['description'])
                )
                messagebox.showinfo("Success", "Brand added successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add brand: {e}")
    
    def add_sub_brand(self):
        """Add new sub brand"""
        dialog = SubBrandDialog(self.parent, "Add Sub Brand")
        if dialog.result:
            try:
                db.execute_insert(
                    "INSERT INTO sub_brands (sub_brand_name, brand_id, description) VALUES (?, ?, ?)",
                    (dialog.result['name'], dialog.result['brand_id'], dialog.result['description'])
                )
                messagebox.showinfo("Success", "Sub Brand added successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sub brand: {e}")
    
    def edit_item(self):
        """Edit selected item"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        # Get selected item data
        item_values = self.data_tree.item(selection[0], 'values')
        
        if self.current_tab == "products":
            self.edit_product(item_values)
        elif self.current_tab == "categories":
            self.edit_category(item_values)
        elif self.current_tab == "sub_categories":
            self.edit_sub_category(item_values)
        elif self.current_tab == "brands":
            self.edit_brand(item_values)
        elif self.current_tab == "sub_brands":
            self.edit_sub_brand(item_values)
    
    def edit_product(self, item_values):
        """Edit product"""
        sku = item_values[0]
        # Get full product data
        product_query = "SELECT * FROM products WHERE sku = ?"
        product_result = db.execute_query(product_query, (sku,))
        
        if product_result:
            product = product_result[0]
            dialog = ProductDialog(self.parent, "Edit Product", product)
            if dialog.result:
                try:
                    db.execute_update(
                        """UPDATE products SET name=?, category_id=?, sub_category_id=?, brand_id=?, sub_brand_id=?, description=?,
                                             stock=?, price_normal=?, price_workshop=?, cost_price=?, reorder_level=?
                           WHERE sku=?""",
                        (dialog.result['name'], dialog.result['category_id'], dialog.result['sub_category_id'],
                         dialog.result['brand_id'], dialog.result['sub_brand_id'],
                         dialog.result['description'], dialog.result['stock'], dialog.result['price_normal'],
                         dialog.result['price_workshop'], dialog.result['cost_price'], dialog.result['reorder_level'], sku)
                    )
                    messagebox.showinfo("Success", "Product updated successfully!")
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update product: {e}")
    
    def edit_category(self, item_values):
        """Edit category"""
        category_id = item_values[0]
        current_name = item_values[1]
        current_desc = item_values[2] if item_values[2] != "N/A" else ""
        
        category_data = {
            'category_id': category_id,
            'category_name': current_name,
            'description': current_desc
        }
        
        dialog = CategoryDialog(self.parent, "Edit Category", category_data)
        if dialog.result:
            try:
                db.execute_update(
                    "UPDATE categories SET category_name=?, description=? WHERE category_id=?",
                    (dialog.result['name'], dialog.result['description'], category_id)
                )
                messagebox.showinfo("Success", "Category updated successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update category: {e}")
    
    def edit_sub_category(self, item_values):
        """Edit sub category"""
        sub_category_id = item_values[0]
        current_name = item_values[1]
        current_category = item_values[2]
        current_desc = item_values[3] if item_values[3] != "N/A" else ""
        
        # Get full data
        sc_data = db.execute_query("SELECT * FROM sub_categories WHERE sub_category_id = ?", (sub_category_id,))
        if sc_data:
            sc_data = sc_data[0]
            sc_data['sub_category_name'] = current_name
            sc_data['category_name'] = current_category
            sc_data['description'] = current_desc
        else:
            sc_data = {
                'sub_category_id': sub_category_id,
                'sub_category_name': current_name,
                'category_name': current_category,
                'description': current_desc
            }
        
        dialog = SubCategoryDialog(self.parent, "Edit Sub Category", sc_data)
        if dialog.result:
            try:
                db.execute_update(
                    "UPDATE sub_categories SET sub_category_name=?, category_id=?, description=? WHERE sub_category_id=?",
                    (dialog.result['name'], dialog.result['category_id'], dialog.result['description'], sub_category_id)
                )
                messagebox.showinfo("Success", "Sub Category updated successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update sub category: {e}")
    
    def edit_brand(self, item_values):
        """Edit brand"""
        brand_id = item_values[0]
        current_name = item_values[1]
        current_desc = item_values[2] if item_values[2] != "N/A" else ""
        
        brand_data = {
            'brand_id': brand_id,
            'brand_name': current_name,
            'description': current_desc
        }
        
        dialog = BrandDialog(self.parent, "Edit Brand", brand_data)
        if dialog.result:
            try:
                db.execute_update(
                    "UPDATE brands SET brand_name=?, description=? WHERE brand_id=?",
                    (dialog.result['name'], dialog.result['description'], brand_id)
                )
                messagebox.showinfo("Success", "Brand updated successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update brand: {e}")
    
    def edit_sub_brand(self, item_values):
        """Edit sub brand"""
        sub_brand_id = item_values[0]
        current_name = item_values[1]
        current_brand = item_values[2]
        current_desc = item_values[3] if item_values[3] != "N/A" else ""
        
        # Get full data
        sb_data = db.execute_query("SELECT * FROM sub_brands WHERE sub_brand_id = ?", (sub_brand_id,))
        if sb_data:
            sb_data = sb_data[0]
            sb_data['sub_brand_name'] = current_name
            sb_data['brand_name'] = current_brand
            sb_data['description'] = current_desc
        else:
            sb_data = {
                'sub_brand_id': sub_brand_id,
                'sub_brand_name': current_name,
                'brand_name': current_brand,
                'description': current_desc
            }
        
        dialog = SubBrandDialog(self.parent, "Edit Sub Brand", sb_data)
        if dialog.result:
            try:
                db.execute_update(
                    "UPDATE sub_brands SET sub_brand_name=?, brand_id=?, description=? WHERE sub_brand_id=?",
                    (dialog.result['name'], dialog.result['brand_id'], dialog.result['description'], sub_brand_id)
                )
                messagebox.showinfo("Success", "Sub Brand updated successfully!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update sub brand: {e}")
    
    def delete_item(self):
        """Delete selected item"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            return
        
        item_values = self.data_tree.item(selection[0], 'values')
        
        try:
            if self.current_tab == "products":
                sku = item_values[0]
                db.execute_update("UPDATE products SET is_active=0 WHERE sku=?", (sku,))
            elif self.current_tab == "categories":
                category_id = item_values[0]
                db.execute_update("DELETE FROM categories WHERE category_id=?", (category_id,))
            elif self.current_tab == "sub_categories":
                sub_category_id = item_values[0]
                db.execute_update("DELETE FROM sub_categories WHERE sub_category_id=?", (sub_category_id,))
            elif self.current_tab == "brands":
                brand_id = item_values[0]
                db.execute_update("DELETE FROM brands WHERE brand_id=?", (brand_id,))
            elif self.current_tab == "sub_brands":
                sub_brand_id = item_values[0]
                db.execute_update("DELETE FROM sub_brands WHERE sub_brand_id=?", (sub_brand_id,))
            
            messagebox.showinfo("Success", "Item deleted successfully!")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {e}")
    
    def export_to_excel(self):
        """Export inventory to Excel"""
        if self.current_tab != "products":
            messagebox.showinfo("Info", "Excel export is only available for Products tab.")
            return
        
        ExportManager.export_inventory_to_excel(
            filter_category=self.category_filter_var.get(),
            filter_brand=self.brand_filter_var.get(),
            filter_stock=self.stock_filter_var.get()
        )
    
    def export_to_pdf(self):
        """Export inventory to PDF"""
        if self.current_tab != "products":
            messagebox.showinfo("Info", "PDF export is only available for Products tab.")
            return
        
        ExportManager.export_inventory_to_pdf(
            filter_category=self.category_filter_var.get(),
            filter_brand=self.brand_filter_var.get(),
            filter_stock=self.stock_filter_var.get()
        )
    
    def handle_export(self, choice):
        """Handle export dropdown selection"""
        if choice == "Excel":
            self.export_to_excel()
        elif choice == "PDF":
            self.export_to_pdf()
        # Reset dropdown to default
        self.export_menu.set("Export")


class ProductDialog:
    def __init__(self, parent, title, product_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x750")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 50))
        
        # Load categories and brands
        self.load_categories_and_brands()
        
        # Create form
        self.create_form(product_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def load_categories_and_brands(self):
        """Load categories and brands for dropdowns"""
        self.categories = db.execute_query("SELECT category_id, category_name FROM categories ORDER BY category_name")
        self.brands = db.execute_query("SELECT brand_id, brand_name FROM brands ORDER BY brand_name")
        self.sub_categories = db.execute_query("SELECT sub_category_id, sub_category_name, category_id FROM sub_categories ORDER BY sub_category_name")
        self.sub_brands = db.execute_query("SELECT sub_brand_id, sub_brand_name, brand_id FROM sub_brands ORDER BY sub_brand_name")
    
    def create_form(self, product_data):
        """Create product form"""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form fields
        # Name
        ctk.CTkLabel(main_frame, text="Product Name:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(main_frame, width=400)
        self.name_entry.pack(anchor="w", pady=(0, 10))
        
        # Category with searchable dropdown
        ctk.CTkLabel(main_frame, text="Category:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.category_dropdown = SearchableDropdown(main_frame, self.categories, 'category_name', 'category_id', 
                                                     placeholder="Select Category...", width=400, height=35,
                                                     command=self.on_category_selected,
                                                     add_command=self.add_category_from_dropdown)
        self.category_dropdown.pack(fill="x", pady=(0, 10))
        
        # Sub Category with searchable dropdown - initialize with all sub categories
        ctk.CTkLabel(main_frame, text="Sub Category:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.sub_category_dropdown = SearchableDropdown(main_frame, self.sub_categories, 'sub_category_name', 'sub_category_id',
                                                         placeholder="Select Sub Category...", width=400, height=35,
                                                         add_command=self.add_sub_category_from_dropdown)
        self.sub_category_dropdown.pack(fill="x", pady=(0, 10))
        
        # Brand with searchable dropdown
        ctk.CTkLabel(main_frame, text="Brand:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.brand_dropdown = SearchableDropdown(main_frame, self.brands, 'brand_name', 'brand_id',
                                                  placeholder="Select Brand...", width=400, height=35,
                                                  command=self.on_brand_selected,
                                                  add_command=self.add_brand_from_dropdown)
        self.brand_dropdown.pack(fill="x", pady=(0, 10))
        
        # Sub Brand with searchable dropdown - initialize with all sub brands
        ctk.CTkLabel(main_frame, text="Sub Brand:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.sub_brand_dropdown = SearchableDropdown(main_frame, self.sub_brands, 'sub_brand_name', 'sub_brand_id',
                                                      placeholder="Select Sub Brand...", width=400, height=35,
                                                      add_command=self.add_sub_brand_from_dropdown)
        self.sub_brand_dropdown.pack(fill="x", pady=(0, 10))
        
        # Description
        ctk.CTkLabel(main_frame, text="Description:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.description_entry = ctk.CTkEntry(main_frame, width=400)
        self.description_entry.pack(anchor="w", pady=(0, 10))
        
        # Stock
        ctk.CTkLabel(main_frame, text="Stock Quantity:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.stock_entry = ctk.CTkEntry(main_frame, width=400)
        self.stock_entry.pack(anchor="w", pady=(0, 10))
        
        # Cost Price
        ctk.CTkLabel(main_frame, text="Cost Price:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.cost_entry = ctk.CTkEntry(main_frame, width=400)
        self.cost_entry.pack(anchor="w", pady=(0, 10))
        
        # Normal Price
        ctk.CTkLabel(main_frame, text="Normal Price:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.normal_price_entry = ctk.CTkEntry(main_frame, width=400)
        self.normal_price_entry.pack(anchor="w", pady=(0, 10))
        
        # Workshop Price
        ctk.CTkLabel(main_frame, text="Workshop Price:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.workshop_price_entry = ctk.CTkEntry(main_frame, width=400)
        self.workshop_price_entry.pack(anchor="w", pady=(0, 10))
        
        # Reorder Level
        ctk.CTkLabel(main_frame, text="Reorder Level:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.reorder_entry = ctk.CTkEntry(main_frame, width=400)
        self.reorder_entry.pack(anchor="w", pady=(0, 10))
        
        # Fill form if editing
        if product_data:
            # Handle SQLite Row objects by accessing columns directly
            self.name_entry.insert(0, product_data['name'] if product_data['name'] else '')
            self.description_entry.insert(0, product_data['description'] if product_data['description'] else '')
            self.stock_entry.insert(0, str(product_data['stock']) if product_data['stock'] else '')
            self.cost_entry.insert(0, str(product_data['cost_price']) if product_data['cost_price'] else '')
            self.normal_price_entry.insert(0, str(product_data['price_normal']) if product_data['price_normal'] else '')
            self.workshop_price_entry.insert(0, str(product_data['price_workshop']) if product_data['price_workshop'] else '')
            self.reorder_entry.insert(0, str(product_data['reorder_level']) if product_data['reorder_level'] else '')
            
            # Set dropdowns
            if product_data['category_id']:
                for cat in self.categories:
                    if cat['category_id'] == product_data['category_id']:
                        self.category_dropdown.set(cat['category_name'], cat['category_id'])
                        # Update sub categories based on selected category
                        self._update_sub_categories(cat['category_id'])
                        break
            
            if product_data['sub_category_id']:
                for sc in self.sub_categories:
                    if sc['sub_category_id'] == product_data['sub_category_id']:
                        self.sub_category_dropdown.set(sc['sub_category_name'], sc['sub_category_id'])
                        break
            
            if product_data['brand_id']:
                for brand in self.brands:
                    if brand['brand_id'] == product_data['brand_id']:
                        self.brand_dropdown.set(brand['brand_name'], brand['brand_id'])
                        # Update sub brands based on selected brand
                        self._update_sub_brands(brand['brand_id'])
                        break
            
            if product_data['sub_brand_id']:
                for sb in self.sub_brands:
                    if sb['sub_brand_id'] == product_data['sub_brand_id']:
                        self.sub_brand_dropdown.set(sb['sub_brand_name'], sb['sub_brand_id'])
                        break
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_product,
            fg_color="green",
            hover_color="darkgreen",
            width=100
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=100
        )
        cancel_btn.pack(side="left")
    
    def on_category_selected(self):
        """Handle category selection - update sub categories"""
        category_id = self.category_dropdown.get()
        if category_id:
            self._update_sub_categories(category_id)
        else:
            self.sub_category_dropdown.set_items([])
            self.sub_category_dropdown.clear()
    
    def on_brand_selected(self):
        """Handle brand selection - update sub brands"""
        brand_id = self.brand_dropdown.get()
        if brand_id:
            self._update_sub_brands(brand_id)
        else:
            self.sub_brand_dropdown.set_items([])
            self.sub_brand_dropdown.clear()
    
    def _update_sub_categories(self, category_id):
        """Update sub categories based on selected category"""
        filtered_sub_categories = [sc for sc in self.sub_categories if sc['category_id'] == category_id]
        self.sub_category_dropdown.set_items(filtered_sub_categories)
        self.sub_category_dropdown.clear()
    
    def _update_sub_brands(self, brand_id):
        """Update sub brands based on selected brand"""
        filtered_sub_brands = [sb for sb in self.sub_brands if sb['brand_id'] == brand_id]
        self.sub_brand_dropdown.set_items(filtered_sub_brands)
        self.sub_brand_dropdown.clear()

    def add_category_from_dropdown(self):
        """Add new category from dropdown"""
        dialog = CategoryDialog(self.dialog, "Add Category")
        if dialog.result:
            try:
                # Insert category
                category_id = db.execute_insert(
                    "INSERT INTO categories (category_name, description) VALUES (?, ?)",
                    (dialog.result['name'], dialog.result['description'])
                )
                # Reload categories
                self.categories = db.execute_query("SELECT category_id, category_name FROM categories ORDER BY category_name")
                # Update dropdown
                self.category_dropdown.set_items(self.categories)
                # Select the new category
                self.category_dropdown.set(dialog.result['name'], category_id)
                # Trigger category selection to update sub categories
                self.on_category_selected()
                messagebox.showinfo("Success", "Category added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add category: {e}")

    def add_brand_from_dropdown(self):
        """Add new brand from dropdown"""
        dialog = BrandDialog(self.dialog, "Add Brand")
        if dialog.result:
            try:
                # Insert brand
                brand_id = db.execute_insert(
                    "INSERT INTO brands (brand_name, description) VALUES (?, ?)",
                    (dialog.result['name'], dialog.result['description'])
                )
                # Reload brands
                self.brands = db.execute_query("SELECT brand_id, brand_name FROM brands ORDER BY brand_name")
                # Update dropdown
                self.brand_dropdown.set_items(self.brands)
                # Select the new brand
                self.brand_dropdown.set(dialog.result['name'], brand_id)
                # Trigger brand selection to update sub brands
                self.on_brand_selected()
                messagebox.showinfo("Success", "Brand added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add brand: {e}")

    def add_sub_category_from_dropdown(self):
        """Add new sub category from dropdown"""
        # Get currently selected category
        category_id = self.category_dropdown.get()
        if not category_id:
            messagebox.showwarning("Warning", "Please select a category first.")
            return
        
        # Get category name for pre-filling
        category_name = self.category_dropdown.get_name()
        
        dialog = SubCategoryDialog(self.dialog, "Add Sub Category", 
                                   sub_category_data={'category_id': category_id, 'category_name': category_name})
        if dialog.result:
            try:
                # Insert sub category
                sub_category_id = db.execute_insert(
                    "INSERT INTO sub_categories (sub_category_name, category_id, description) VALUES (?, ?, ?)",
                    (dialog.result['name'], dialog.result['category_id'], dialog.result['description'])
                )
                # Reload sub categories
                self.sub_categories = db.execute_query("SELECT sub_category_id, sub_category_name, category_id FROM sub_categories ORDER BY sub_category_name")
                # Update dropdown with filtered items
                self._update_sub_categories(category_id)
                # Select the new sub category
                self.sub_category_dropdown.set(dialog.result['name'], sub_category_id)
                messagebox.showinfo("Success", "Sub Category added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sub category: {e}")

    def add_sub_brand_from_dropdown(self):
        """Add new sub brand from dropdown"""
        # Get currently selected brand
        brand_id = self.brand_dropdown.get()
        if not brand_id:
            messagebox.showwarning("Warning", "Please select a brand first.")
            return
        
        # Get brand name for pre-filling
        brand_name = self.brand_dropdown.get_name()
        
        dialog = SubBrandDialog(self.dialog, "Add Sub Brand",
                               sub_brand_data={'brand_id': brand_id, 'brand_name': brand_name})
        if dialog.result:
            try:
                # Insert sub brand
                sub_brand_id = db.execute_insert(
                    "INSERT INTO sub_brands (sub_brand_name, brand_id, description) VALUES (?, ?, ?)",
                    (dialog.result['name'], dialog.result['brand_id'], dialog.result['description'])
                )
                # Reload sub brands
                self.sub_brands = db.execute_query("SELECT sub_brand_id, sub_brand_name, brand_id FROM sub_brands ORDER BY sub_brand_name")
                # Update dropdown with filtered items
                self._update_sub_brands(brand_id)
                # Select the new sub brand
                self.sub_brand_dropdown.set(dialog.result['name'], sub_brand_id)
                messagebox.showinfo("Success", "Sub Brand added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sub brand: {e}")

    def save_product(self):
        """Save product data"""
        try:
            # Validate required fields
            if not self.name_entry.get():
                messagebox.showerror("Error", "Product name is required")
                return
            
            # Get category and brand IDs from dropdowns
            category_id = self.category_dropdown.get()
            sub_category_id = self.sub_category_dropdown.get()
            brand_id = self.brand_dropdown.get()
            sub_brand_id = self.sub_brand_dropdown.get()
            
            # Validate numeric fields
            stock = int(self.stock_entry.get() or 0)
            cost_price = float(self.cost_entry.get() or 0)
            price_normal = float(self.normal_price_entry.get() or 0)
            price_workshop = float(self.workshop_price_entry.get() or 0)
            reorder_level = int(self.reorder_entry.get() or 10)
            
            # Data validation - prevent negative stock
            if stock < 0:
                messagebox.showerror("Validation Error", "Stock quantity cannot be negative!")
                return
            if cost_price < 0:
                messagebox.showerror("Validation Error", "Cost price cannot be negative!")
                return
            if price_normal < 0:
                messagebox.showerror("Validation Error", "Normal price cannot be negative!")
                return
            if price_workshop < 0:
                messagebox.showerror("Validation Error", "Workshop price cannot be negative!")
                return
            if reorder_level < 0:
                messagebox.showerror("Validation Error", "Reorder level cannot be negative!")
                return
            
            self.result = {
                'name': self.name_entry.get(),
                'category_id': category_id,
                'sub_category_id': sub_category_id,
                'brand_id': brand_id,
                'sub_brand_id': sub_brand_id,
                'description': self.description_entry.get(),
                'stock': stock,
                'cost_price': cost_price,
                'price_normal': price_normal,
                'price_workshop': price_workshop,
                'reorder_level': reorder_level
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for prices and quantities")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving product: {e}")


class CategoryDialog:
    def __init__(self, parent, title, category_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        # Calculate position to center on parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 500
        dialog_height = 400
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Ensure dialog stays on top
        self.dialog.attributes("-topmost", True)
        self.dialog.focus_force()
        
        # Create form
        self.create_form(category_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self, category_data):
        """Create category form with modern styling"""
        # Main container - scrollable to ensure all content is visible
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with icon
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#4CAF50")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        category_icon = ctk.CTkLabel(header_frame, text="Category", font=ctk.CTkFont(size=24))
        category_icon.pack(pady=(10, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Category Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=(0, 10))
        
        # Form fields container
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Name field
        name_label = ctk.CTkLabel(
            fields_frame,
            text="Category Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Enter category name...",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Description field
        desc_label = ctk.CTkLabel(
            fields_frame,
            text="Description (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        desc_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.description_textbox = ctk.CTkTextbox(
            fields_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.description_textbox.pack(fill="x", padx=15, pady=(0, 15))
        
        # Fill form if editing
        if category_data:
            self.name_entry.insert(0, category_data.get('category_name', ''))
            if category_data.get('description'):
                self.description_textbox.insert("1.0", category_data['description'])
        
        # Buttons container
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Category",
            command=self.save_category,
            width=140,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_btn.pack(side="left", padx=15, pady=15)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            height=40,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cancel_btn.pack(side="right", padx=15, pady=15)
        
        # Focus on name entry
        self.dialog.after(100, lambda: self.name_entry.focus())
    
    def save_category(self):
        """Save category with validation"""
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Category name is required.")
                return
            
            description = self.description_textbox.get("1.0", "end-1c").strip()
            
            self.result = {
                'name': name,
                'description': description or ""
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()


class SubCategoryDialog:
    def __init__(self, parent, title, sub_category_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
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
        
        self.dialog.attributes("-topmost", True)
        self.dialog.focus_force()
        
        # Load categories
        self.categories = db.execute_query("SELECT category_id, category_name FROM categories ORDER BY category_name")
        
        # Create form
        self.create_form(sub_category_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self, sub_category_data):
        """Create sub category form with modern styling"""
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#8BC34A")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Sub Category Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        # Form fields container
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Category selection
        cat_label = ctk.CTkLabel(
            fields_frame,
            text="Parent Category:*",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cat_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.category_var = tk.StringVar()
        self.category_id_var = tk.IntVar()
        category_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        category_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.category_display = ctk.CTkEntry(category_frame, width=320, state="readonly", font=ctk.CTkFont(size=12))
        self.category_display.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(category_frame, text="Search", width=70, command=self.show_category_selector).pack(side="left")
        
        # Name field
        name_label = ctk.CTkLabel(
            fields_frame,
            text="Sub Category Name:*",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Enter sub category name...",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Description field
        desc_label = ctk.CTkLabel(
            fields_frame,
            text="Description (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        desc_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.description_textbox = ctk.CTkTextbox(
            fields_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.description_textbox.pack(fill="x", padx=15, pady=(0, 15))
        
        # Fill form if editing
        if sub_category_data:
            self.name_entry.insert(0, sub_category_data.get('sub_category_name', ''))
            if sub_category_data.get('description'):
                self.description_textbox.insert("1.0", sub_category_data['description'])
            
            # Set category
            if sub_category_data.get('category_id'):
                for cat in self.categories:
                    if cat['category_id'] == sub_category_data['category_id']:
                        self.category_id_var.set(cat['category_id'])
                        self.category_display.configure(state="normal")
                        self.category_display.delete(0, "end")
                        self.category_display.insert(0, cat['category_name'])
                        self.category_display.configure(state="readonly")
                        break
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Sub Category",
            command=self.save_sub_category,
            width=160,
            height=40,
            fg_color="#8BC34A",
            hover_color="#7CB342",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_btn.pack(side="left", padx=15, pady=15)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            height=40,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cancel_btn.pack(side="right", padx=15, pady=15)
        
        self.dialog.after(100, lambda: self.name_entry.focus())
    
    def show_category_selector(self):
        """Show category selector"""
        selector = SelectionDialog(self.dialog, "Select Category", self.categories, 'category_name', 'category_id')
        if selector.result:
            self.category_id_var.set(selector.result['id'])
            self.category_display.configure(state="normal")
            self.category_display.delete(0, "end")
            self.category_display.insert(0, selector.result['name'])
            self.category_display.configure(state="readonly")
    
    def save_sub_category(self):
        """Save sub category"""
        try:
            name = self.name_entry.get().strip()
            category_id = self.category_id_var.get()
            
            if not name:
                messagebox.showerror("Error", "Sub Category name is required.")
                return
            if not category_id:
                messagebox.showerror("Error", "Please select a parent category.")
                return
            
            description = self.description_textbox.get("1.0", "end-1c").strip()
            
            self.result = {
                'name': name,
                'category_id': category_id,
                'description': description or ""
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()


class BrandDialog:
    def __init__(self, parent, title, brand_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 500
        dialog_height = 400
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        self.dialog.attributes("-topmost", True)
        self.dialog.focus_force()
        
        # Create form
        self.create_form(brand_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self, brand_data):
        """Create brand form with modern styling"""
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#FF9800")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Brand Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        # Form fields container
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Name field
        name_label = ctk.CTkLabel(
            fields_frame,
            text="Brand Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Enter brand name...",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Description field
        desc_label = ctk.CTkLabel(
            fields_frame,
            text="Description (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        desc_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.description_textbox = ctk.CTkTextbox(
            fields_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.description_textbox.pack(fill="x", padx=15, pady=(0, 15))
        
        # Fill form if editing
        if brand_data:
            self.name_entry.insert(0, brand_data.get('brand_name', ''))
            if brand_data.get('description'):
                self.description_textbox.insert("1.0", brand_data['description'])
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Brand",
            command=self.save_brand,
            width=140,
            height=40,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_btn.pack(side="left", padx=15, pady=15)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            height=40,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cancel_btn.pack(side="right", padx=15, pady=15)
        
        self.dialog.after(100, lambda: self.name_entry.focus())
    
    def save_brand(self):
        """Save brand"""
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Brand name is required.")
                return
            
            description = self.description_textbox.get("1.0", "end-1c").strip()
            
            self.result = {
                'name': name,
                'description': description or ""
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()


class SubBrandDialog:
    def __init__(self, parent, title, sub_brand_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
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
        
        self.dialog.attributes("-topmost", True)
        self.dialog.focus_force()
        
        # Load brands
        self.brands = db.execute_query("SELECT brand_id, brand_name FROM brands ORDER BY brand_name")
        
        # Create form
        self.create_form(sub_brand_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self, sub_brand_data):
        """Create sub brand form"""
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#FFB74D")
        header_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Sub Brand Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        # Form fields
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Brand selection
        brand_label = ctk.CTkLabel(
            fields_frame,
            text="Parent Brand:*",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        brand_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.brand_var = tk.StringVar()
        self.brand_id_var = tk.IntVar()
        brand_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        brand_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.brand_display = ctk.CTkEntry(brand_frame, width=320, state="readonly", font=ctk.CTkFont(size=12))
        self.brand_display.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(brand_frame, text="Search", width=70, command=self.show_brand_selector).pack(side="left")
        
        # Name field
        name_label = ctk.CTkLabel(
            fields_frame,
            text="Sub Brand Name:*",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Enter sub brand name...",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Description field
        desc_label = ctk.CTkLabel(
            fields_frame,
            text="Description (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        desc_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.description_textbox = ctk.CTkTextbox(
            fields_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.description_textbox.pack(fill="x", padx=15, pady=(0, 15))
        
        # Fill form if editing
        if sub_brand_data:
            self.name_entry.insert(0, sub_brand_data.get('sub_brand_name', ''))
            if sub_brand_data.get('description'):
                self.description_textbox.insert("1.0", sub_brand_data['description'])
            
            # Set brand
            if sub_brand_data.get('brand_id'):
                for brand in self.brands:
                    if brand['brand_id'] == sub_brand_data['brand_id']:
                        self.brand_id_var.set(brand['brand_id'])
                        self.brand_display.configure(state="normal")
                        self.brand_display.delete(0, "end")
                        self.brand_display.insert(0, brand['brand_name'])
                        self.brand_display.configure(state="readonly")
                        break
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Sub Brand",
            command=self.save_sub_brand,
            width=160,
            height=40,
            fg_color="#FFB74D",
            hover_color="#FFA726",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_btn.pack(side="left", padx=15, pady=15)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            height=40,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cancel_btn.pack(side="right", padx=15, pady=15)
        
        self.dialog.after(100, lambda: self.name_entry.focus())
    
    def show_brand_selector(self):
        """Show brand selector"""
        selector = SelectionDialog(self.dialog, "Select Brand", self.brands, 'brand_name', 'brand_id')
        if selector.result:
            self.brand_id_var.set(selector.result['id'])
            self.brand_display.configure(state="normal")
            self.brand_display.delete(0, "end")
            self.brand_display.insert(0, selector.result['name'])
            self.brand_display.configure(state="readonly")
    
    def save_sub_brand(self):
        """Save sub brand"""
        try:
            name = self.name_entry.get().strip()
            brand_id = self.brand_id_var.get()
            
            if not name:
                messagebox.showerror("Error", "Sub Brand name is required.")
                return
            if not brand_id:
                messagebox.showerror("Error", "Please select a parent brand.")
                return
            
            description = self.description_textbox.get("1.0", "end-1c").strip()
            
            self.result = {
                'name': name,
                'brand_id': brand_id,
                'description': description or ""
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()


class SearchableDropdown(ctk.CTkFrame):
    """Custom searchable dropdown component combining dropdown and search"""
    def __init__(self, parent, items, name_field, id_field, placeholder="Select...", 
                 width=400, height=35, command=None, add_command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.items = items
        self.name_field = name_field
        self.id_field = id_field
        self.command = command
        self.add_command = add_command
        self.selected_id = None
        self.selected_name = None
        self.dropdown_open = False
        
        # Main container frame
        self.container = ctk.CTkFrame(self, fg_color=("white", "#2D2D2D"), 
                                       border_color=("#D1D5DB", "#404040"),
                                       border_width=1, corner_radius=6)
        self.container.pack(fill="both", expand=True)
        
        # Display label (shows selected value)
        self.display_var = tk.StringVar(value=placeholder)
        self.display_label = ctk.CTkLabel(self.container, textvariable=self.display_var,
                                          font=ctk.CTkFont(size=12),
                                          text_color=("gray40", "gray70"),
                                          width=width-60, anchor="w")
        self.display_label.pack(side="left", padx=(12, 5), pady=5)
        
        # Dropdown button with chevron
        self.dropdown_btn = ctk.CTkButton(self.container, text="▼", width=30, height=height-4,
                                          fg_color="transparent", text_color=("gray40", "gray70"),
                                          hover_color=("gray85", "gray35"),
                                          command=self.toggle_dropdown)
        self.dropdown_btn.pack(side="right", padx=(0, 3), pady=3)
        
        # Make the entire container clickable
        self.container.bind("<Button-1>", lambda e: self.toggle_dropdown())
        self.display_label.bind("<Button-1>", lambda e: self.toggle_dropdown())
        
        # Dropdown window (created when needed)
        self.dropdown_window = None
        self.search_var = None
        self.listbox = None
        self.filtered_items = items.copy()
    
    def set_items(self, items):
        """Update the items in the dropdown"""
        self.items = items
        self.filtered_items = items.copy()
    
    def get(self):
        """Get the selected value"""
        return self.selected_id
    
    def get_name(self):
        """Get the selected name"""
        return self.selected_name
    
    def set(self, name, id_value):
        """Set the selected value"""
        self.selected_name = name
        self.selected_id = id_value
        self.display_var.set(name)
        self.display_label.configure(text_color=("gray10", "gray90"))
    
    def clear(self):
        """Clear the selection"""
        self.selected_name = None
        self.selected_id = None
        self.display_var.set("Select...")
        self.display_label.configure(text_color=("gray40", "gray70"))
    
    def toggle_dropdown(self):
        """Toggle the dropdown window"""
        if self.dropdown_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self):
        """Open the dropdown window with search and list"""
        if self.dropdown_open:
            return
        
        self.dropdown_open = True
        self.dropdown_btn.configure(text="▲")
        
        # Create dropdown window
        self.dropdown_window = ctk.CTkToplevel(self.winfo_toplevel())
        self.dropdown_window.overrideredirect(True)  # Remove window decorations
        self.dropdown_window.attributes("-topmost", True)
        
        # Position dropdown below the container
        x = self.container.winfo_rootx()
        y = self.container.winfo_rooty() + self.container.winfo_height() + 2
        width = self.container.winfo_width()
        
        self.dropdown_window.geometry(f"{width}x350+{x}+{y}")
        
        # Dropdown frame
        dropdown_frame = ctk.CTkFrame(self.dropdown_window, fg_color=("white", "#2D2D2D"),
                                       border_color=("#D1D5DB", "#404040"),
                                       border_width=1, corner_radius=6)
        dropdown_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Search frame
        search_frame = ctk.CTkFrame(dropdown_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Search icon
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=12))
        search_icon.pack(side="left", padx=(0, 5))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_items)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, 
                                    placeholder_text="Search...",
                                    font=ctk.CTkFont(size=12),
                                    height=32, border_width=0)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.focus()
        
        # Separator
        separator = ctk.CTkFrame(dropdown_frame, height=1, fg_color=(("#E5E7EB", "#404040")))
        separator.pack(fill="x", padx=10, pady=5)
        
        # Add New button (if add_command is provided)
        if hasattr(self, 'add_command') and self.add_command:
            add_btn = ctk.CTkButton(dropdown_frame, text="+ Add New", width=100, height=28,
                                    fg_color="#3B82F6", hover_color="#2563EB",
                                    font=ctk.CTkFont(size=11), command=self._on_add_new)
            add_btn.pack(anchor="w", padx=10, pady=(0, 5))
            
            separator2 = ctk.CTkFrame(dropdown_frame, height=1, fg_color=(("#E5E7EB", "#404040")))
            separator2.pack(fill="x", padx=10, pady=5)
        
        # List frame
        list_frame = ctk.CTkFrame(dropdown_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox
        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 12), 
                                   bg="#2D2D2D" if ctk.get_appearance_mode() == "Dark" else "white",
                                   fg="white" if ctk.get_appearance_mode() == "Dark" else "black",
                                   selectbackground="#3B82F6", 
                                   selectforeground="white",
                                   borderwidth=0, highlightthickness=0,
                                   activestyle="none",
                                   yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.listbox.yview)
        
        # Bind events
        self.listbox.bind("<Double-1>", lambda e: self._select_item())
        self.listbox.bind("<Return>", lambda e: self._select_item())
        self.listbox.bind("<Button-1>", lambda e: self._on_list_click(e))
        
        # Close on escape or click outside
        self.dropdown_window.bind("<Escape>", lambda e: self.close_dropdown())
        self.dropdown_window.bind("<FocusOut>", lambda e: self._on_focus_out())
        
        # Populate list
        self._populate_list()
        
        # Bind click outside to close
        self.winfo_toplevel().bind("<Button-1>", self._on_click_outside, add="+")
    
    def close_dropdown(self):
        """Close the dropdown window"""
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
        self.dropdown_open = False
        self.dropdown_btn.configure(text="▼")
        self.winfo_toplevel().unbind("<Button-1>")
    
    def _on_click_outside(self, event):
        """Handle click outside dropdown"""
        if self.dropdown_window:
            # Check if click is outside dropdown
            x = self.dropdown_window.winfo_rootx()
            y = self.dropdown_window.winfo_rooty()
            width = self.dropdown_window.winfo_width()
            height = self.dropdown_window.winfo_height()
            
            if not (x <= event.x_root <= x + width and y <= event.y_root <= y + height):
                # Also check if click is on the container
                cx = self.container.winfo_rootx()
                cy = self.container.winfo_rooty()
                cw = self.container.winfo_width()
                ch = self.container.winfo_height()
                
                if not (cx <= event.x_root <= cx + cw and cy <= event.y_root <= cy + ch):
                    self.close_dropdown()
    
    def _on_focus_out(self):
        """Handle focus out event"""
        self.winfo_toplevel().after(100, self._check_focus)
    
    def _check_focus(self):
        """Check if focus is still in dropdown"""
        if self.dropdown_window and not self.dropdown_window.focus_get():
            self.close_dropdown()
    
    def _populate_list(self):
        """Populate the listbox with items"""
        self.listbox.delete(0, tk.END)
        for item in self.filtered_items:
            self.listbox.insert(tk.END, item[self.name_field])
        
        # Highlight selected item
        if self.selected_name:
            for i, item in enumerate(self.filtered_items):
                if item[self.name_field] == self.selected_name:
                    self.listbox.selection_set(i)
                    self.listbox.see(i)
                    break
    
    def _filter_items(self, *args):
        """Filter items based on search"""
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            self.filtered_items = self.items.copy()
        else:
            self.filtered_items = [item for item in self.items 
                                   if search_term in item[self.name_field].lower()]
        
        self._populate_list()
    
    def _on_list_click(self, event):
        """Handle list click"""
        # Get the item under cursor
        index = self.listbox.nearest(event.y)
        if 0 <= index < self.listbox.size():
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
    
    def _select_item(self):
        """Select the highlighted item"""
        selection = self.listbox.curselection()
        if not selection:
            return
        
        selected_name = self.listbox.get(selection[0])
        
        # Find the item with matching name
        for item in self.items:
            if item[self.name_field] == selected_name:
                self.set(selected_name, item[self.id_field])
                break
        
        self.close_dropdown()
        
        # Call callback if provided
        if self.command:
            self.command()
    
    def _on_add_new(self):
        """Handle Add New button click"""
        self.close_dropdown()
        if self.add_command:
            self.add_command()


class SelectionDialog:
    """Searchable selection dialog for categories and brands"""
    def __init__(self, parent, title, items, name_field, id_field):
        self.parent = parent
        self.items = items
        self.name_field = name_field
        self.id_field = id_field
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (500 // 2)
        self.dialog.geometry(f"400x500+{x}+{y}")
        
        self.create_ui()
        self.dialog.wait_window()
    
    def create_ui(self):
        """Create the selection UI"""
        # Header
        header = ctk.CTkFrame(self.dialog, corner_radius=0, fg_color="#3B82F6")
        header.pack(fill="x", pady=0)
        ctk.CTkLabel(header, text=self.dialog.title(), font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=15)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_items)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=280, placeholder_text="Type to search...")
        search_entry.pack(side="left")
        
        # List frame
        list_frame = ctk.CTkFrame(self.dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Create listbox with scrollbar
        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 12), bg="#2D2D2D", fg="white",
                                  selectbackground="#3B82F6", selectforeground="white",
                                  borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click
        self.listbox.bind("<Double-1>", lambda e: self.select_item())
        
        # Populate list
        self.populate_list()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(button_frame, text="Select", command=self.select_item, 
                     fg_color="#3B82F6", width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, 
                     fg_color="#6B7280", width=100).pack(side="left")
    
    def populate_list(self):
        """Populate the listbox with items"""
        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, item[self.name_field])
    
    def filter_items(self, *args):
        """Filter items based on search"""
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        
        for item in self.items:
            name = item[self.name_field].lower()
            if search_term in name:
                self.listbox.insert(tk.END, item[self.name_field])
    
    def select_item(self):
        """Select the highlighted item"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        selected_name = self.listbox.get(selection[0])
        
        # Find the item with matching name
        for item in self.items:
            if item[self.name_field] == selected_name:
                self.result = {'id': item[self.id_field], 'name': selected_name}
                break
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel selection"""
        self.result = None
        self.dialog.destroy()
