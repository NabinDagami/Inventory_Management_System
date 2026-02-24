"""
Table styling utility for consistent table headers across the application
"""
import tkinter as tk
from tkinter import ttk

class TableStyleManager:
    """Centralized manager for table styles to ensure consistent appearance"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self._styles_applied = set()  # Track which styles have been applied
    
    def _get_style(self):
        """Get or create style object"""
        try:
            # Always create a new style instance to ensure it's fresh
            style = ttk.Style()
            # Set theme for consistency
            try:
                style.theme_use('clam')
            except:
                pass
            return style
        except:
            # Fallback if style creation fails
            return None
    
    def _setup_base_styles(self):
        """Setup base styling configurations"""
        # Set theme to ensure compatibility
        try:
            self.style.theme_use('clam')  # Use clam theme for better customization
        except:
            pass
        
        # Configure base treeview style
        self.style.configure("Custom.Treeview",
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white",
                           borderwidth=1,
                           relief="solid")
        
        # Configure base heading style
        self.style.configure("Custom.Treeview.Heading",
                           font=("Arial", 11, "bold"),
                           relief="flat",
                           borderwidth=1)
    
    def apply_product_style(self, treeview):
        """Apply blue styling for products tables"""
        style = self._get_style()
        if not style:
            return None
            
        style_name = "Products.Treeview"
        heading_style = "Products.Treeview.Heading"
        
        # Configure specific style
        style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        style.configure(heading_style,
                           background="#2E86AB",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        style.map(heading_style,
                      background=[("active", "#1E5F7A")],
                      foreground=[("active", "white")])
        
        style.map(style_name,
                      background=[("selected", "#0078D4")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_category_style(self, treeview):
        """Apply green styling for categories tables"""
        self._ensure_style()
        
        style_name = "Categories.Treeview"
        heading_style = "Categories.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#4CAF50",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#45A049")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#4CAF50")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_brand_style(self, treeview):
        """Apply orange styling for brands tables"""
        self._ensure_style()
        
        style_name = "Brands.Treeview"
        heading_style = "Brands.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#FF9800",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#F57C00")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#FF9800")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_sales_style(self, treeview):
        """Apply purple styling for sales tables"""
        self._ensure_style()
        
        style_name = "Sales.Treeview"
        heading_style = "Sales.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#9C27B0",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#7B1FA2")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#9C27B0")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_purchase_style(self, treeview):
        """Apply teal styling for purchase tables"""
        self._ensure_style()
        
        style_name = "Purchases.Treeview"
        heading_style = "Purchases.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#009688",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#00695C")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#009688")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_supplier_style(self, treeview):
        """Apply brown styling for supplier tables"""
        self._ensure_style()
        
        style_name = "Suppliers.Treeview"
        heading_style = "Suppliers.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#795548",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#5D4037")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#795548")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_customer_style(self, treeview):
        """Apply indigo styling for customer tables"""
        self._ensure_style()
        
        style_name = "Customers.Treeview"
        heading_style = "Customers.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#3F51B5",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#303F9F")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#3F51B5")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name
    
    def apply_report_style(self, treeview):
        """Apply dark blue styling for report tables"""
        self._ensure_style()
        
        style_name = "Reports.Treeview"
        heading_style = "Reports.Treeview.Heading"
        
        # Configure specific style
        self.style.configure(style_name,
                           background="white",
                           foreground="black",
                           rowheight=35,
                           fieldbackground="white")
        
        self.style.configure(heading_style,
                           background="#3f51b5",
                           foreground="white",
                           font=("Arial", 11, "bold"),
                           relief="flat")
        
        # Map hover and selection effects
        self.style.map(heading_style,
                      background=[("active", "#303f9f")],
                      foreground=[("active", "white")])
        
        self.style.map(style_name,
                      background=[("selected", "#3f51b5")],
                      foreground=[("selected", "white")])
        
        # Apply style to treeview
        treeview.configure(style=style_name)
        return style_name

# Global instance
table_styles = TableStyleManager()
