"""
Simple table styling utility that applies styles directly to treeviews
without creating conflicting Style objects
"""
from tkinter import ttk

def apply_product_style(treeview):
    """Apply professional styling for products tables"""
    style = ttk.Style()
    
    # Set theme for consistency
    try:
        style.theme_use('clam')
    except:
        pass
    
    # Configure styles - softer gray background to blend with dark UI
    style.configure("ProductsTable.Treeview", 
                   background="#F3F4F6",
                   foreground="#212121",
                   rowheight=60,
                   fieldbackground="#F3F4F6",
                   font=("Segoe UI", 11))
    
    # Flat header design - modern enterprise look
    style.configure("ProductsTable.Treeview.Heading", 
                   background="#2563EB",
                   foreground="white",
                   font=("Segoe UI", 12, "bold"),
                   relief="flat",
                   padding=8)
    
    # Map effects
    style.map("ProductsTable.Treeview.Heading",
             background=[("active", "#1D4ED8")],
             foreground=[("active", "white")])
    
    # Selected row - subtle highlight
    style.map("ProductsTable.Treeview",
             background=[("selected", "#DBEAFE"), ("focus", "#DBEAFE")],
             foreground=[("selected", "#1E40AF"), ("focus", "#1E40AF")])
    
    # Apply to treeview
    treeview.configure(style="ProductsTable.Treeview")

def apply_category_style(treeview):
    """Apply green styling for categories tables"""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure("CategoriesTable.Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=35,
                   fieldbackground="white")
    
    style.configure("CategoriesTable.Treeview.Heading", 
                   background="#4CAF50",
                   foreground="white",
                   font=("Arial", 11, "bold"),
                   relief="flat")
    
    style.map("CategoriesTable.Treeview.Heading",
             background=[("active", "#45A049")],
             foreground=[("active", "white")])
    
    style.map("CategoriesTable.Treeview",
             background=[("selected", "#4CAF50")],
             foreground=[("selected", "white")])
    
    treeview.configure(style="CategoriesTable.Treeview")

def apply_brand_style(treeview):
    """Apply orange styling for brands tables"""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure("BrandsTable.Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=35,
                   fieldbackground="white")
    
    style.configure("BrandsTable.Treeview.Heading", 
                   background="#FF9800",
                   foreground="white",
                   font=("Arial", 11, "bold"),
                   relief="flat")
    
    style.map("BrandsTable.Treeview.Heading",
             background=[("active", "#F57C00")],
             foreground=[("active", "white")])
    
    style.map("BrandsTable.Treeview",
             background=[("selected", "#FF9800")],
             foreground=[("selected", "white")])
    
    treeview.configure(style="BrandsTable.Treeview")

def apply_customer_style(treeview):
    """Apply indigo styling for customer tables"""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure("CustomersTable.Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=35,
                   fieldbackground="white")
    
    style.configure("CustomersTable.Treeview.Heading", 
                   background="#3F51B5",
                   foreground="white",
                   font=("Arial", 11, "bold"),
                   relief="flat")
    
    style.map("CustomersTable.Treeview.Heading",
             background=[("active", "#303F9F")],
             foreground=[("active", "white")])
    
    style.map("CustomersTable.Treeview",
             background=[("selected", "#3F51B5")],
             foreground=[("selected", "white")])
    
    treeview.configure(style="CustomersTable.Treeview")

def apply_supplier_style(treeview):
    """Apply brown styling for supplier tables"""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure("SuppliersTable.Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=35,
                   fieldbackground="white")
    
    style.configure("SuppliersTable.Treeview.Heading", 
                   background="#795548",
                   foreground="white",
                   font=("Arial", 11, "bold"),
                   relief="flat")
    
    style.map("SuppliersTable.Treeview.Heading",
             background=[("active", "#5D4037")],
             foreground=[("active", "white")])
    
    style.map("SuppliersTable.Treeview",
             background=[("selected", "#795548")],
             foreground=[("selected", "white")])
    
    treeview.configure(style="SuppliersTable.Treeview")


# ===== Sales View Styles =====

def apply_sales_history_style(treeview):
    """Apply styling for sales history table"""
    style = ttk.Style()
    style_name = f"SalesHistory{id(treeview)}.Treeview"
    heading_style = f"SalesHistory{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=32,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#e91e63",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#c2185b")])
    
    treeview.configure(style=style_name)


def apply_sales_products_style(treeview):
    """Apply styling for sales products selection table"""
    style = ttk.Style()
    style_name = f"SalesProducts{id(treeview)}.Treeview"
    heading_style = f"SalesProducts{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#2196f3",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#1976d2")])
    
    treeview.configure(style=style_name)


def apply_cart_style(treeview):
    """Apply styling for shopping cart table"""
    style = ttk.Style()
    style_name = f"Cart{id(treeview)}.Treeview"
    heading_style = f"Cart{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#4caf50",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#45a049")])
    
    treeview.configure(style=style_name)


def apply_sale_details_style(treeview):
    """Apply styling for sale details table"""
    style = ttk.Style()
    style_name = f"SaleDetails{id(treeview)}.Treeview"
    heading_style = f"SaleDetails{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#673ab7",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#5e35b1")])
    
    treeview.configure(style=style_name)


# ===== Purchases View Styles =====

def apply_purchase_history_style(treeview):
    """Apply styling for purchase history table"""
    style = ttk.Style()
    style_name = f"PurchaseHistory{id(treeview)}.Treeview"
    heading_style = f"PurchaseHistory{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=32,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#9c27b0",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#7b1fa2")])
    
    treeview.configure(style=style_name)


def apply_purchase_products_style(treeview):
    """Apply styling for purchase products selection table"""
    style = ttk.Style()
    style_name = f"PurchaseProducts{id(treeview)}.Treeview"
    heading_style = f"PurchaseProducts{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#1976d2",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#1565c0")])
    
    treeview.configure(style=style_name)


def apply_purchase_order_style(treeview):
    """Apply styling for purchase order items table"""
    style = ttk.Style()
    style_name = f"PurchaseOrder{id(treeview)}.Treeview"
    heading_style = f"PurchaseOrder{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#ff9800",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#f57c00")])
    
    treeview.configure(style=style_name)


# ===== Reports View Styles =====

def apply_reports_style(treeview):
    """Apply styling for reports tables"""
    style = ttk.Style()
    style_name = f"Reports{id(treeview)}.Treeview"
    heading_style = f"Reports{id(treeview)}.Treeview.Heading"
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure(style_name,
                   background="white",
                   foreground="black",
                   rowheight=30,
                   fieldbackground="white")
    
    style.configure(heading_style,
                   background="#607d8b",
                   foreground="white",
                   font=("Arial", 10, "bold"),
                   relief="flat")
    
    style.map(heading_style,
             background=[("active", "#455a64")])
    
    treeview.configure(style=style_name)
