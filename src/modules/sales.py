import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class SalesModule:
    def __init__(self, parent):
        self.parent = parent
        self.cart_items = []
        self.current_customer = None
        self.create_sales_interface()
        self.load_customers()
        self.load_products()
    
    def create_sales_interface(self):
        """Create the sales management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with customer selection
        header_frame = ctk.CTkFrame(main_frame)
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
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left side - Product selection
        self.create_product_selection(content_frame)
        
        # Right side - Cart and total
        self.create_cart_section(content_frame)
    
    def create_product_selection(self, parent):
        """Create product selection area"""
        product_frame = ctk.CTkFrame(parent)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            product_frame, 
            text="📦 Select Products", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Search box
        search_frame = ctk.CTkFrame(product_frame)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        search_entry = ctk.CTkEntry(
            search_frame, 
            textvariable=self.search_var,
            placeholder_text="Product name or SKU..."
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Products table
        products_table_frame = ctk.CTkFrame(product_frame)
        products_table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview for products
        columns = ("SKU", "Name", "Stock", "Normal Price", "Workshop Price")
        self.products_tree = ttk.Treeview(products_table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)
        
        # Scrollbar for products
        products_scrollbar = ttk.Scrollbar(products_table_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        self.products_tree.pack(side="left", fill="both", expand=True)
        products_scrollbar.pack(side="right", fill="y")
        
        # Add to cart button
        add_button = ctk.CTkButton(
            product_frame,
            text="➕ Add to Cart",
            command=self.add_to_cart,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        add_button.pack(pady=10)
        
        # Bind double-click to add to cart
        self.products_tree.bind("<Double-1>", lambda e: self.add_to_cart())
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        cart_frame = ctk.CTkFrame(parent)
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            cart_frame, 
            text="🛒 Shopping Cart", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Cart items table
        cart_table_frame = ctk.CTkFrame(cart_frame)
        cart_table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview for cart
        cart_columns = ("Product", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_table_frame, columns=cart_columns, show="headings", height=12)
        
        # Define headings
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            if col == "Product":
                self.cart_tree.column(col, width=150)
            else:
                self.cart_tree.column(col, width=80)
        
        # Scrollbar for cart
        cart_scrollbar = ttk.Scrollbar(cart_table_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True)
        cart_scrollbar.pack(side="right", fill="y")
        
        # Cart actions
        actions_frame = ctk.CTkFrame(cart_frame)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        remove_button = ctk.CTkButton(
            actions_frame,
            text="❌ Remove Item",
            command=self.remove_from_cart,
            width=120,
            height=30
        )
        remove_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Clear Cart",
            command=self.clear_cart,
            width=120,
            height=30
        )
        clear_button.pack(side="left", padx=5)
        
        # Totals section
        totals_frame = ctk.CTkFrame(cart_frame)
        totals_frame.pack(fill="x", padx=10, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(
            totals_frame, 
            text="Subtotal: $0.00",
            font=ctk.CTkFont(size=14)
        )
        self.subtotal_label.pack(pady=2)
        
        self.total_label = ctk.CTkLabel(
            totals_frame, 
            text="Total: $0.00",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.total_label.pack(pady=2)
        
        # Process sale button
        process_button = ctk.CTkButton(
            cart_frame,
            text="💰 Process Sale",
            command=self.process_sale,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="green",
            hover_color="darkgreen"
        )
        process_button.pack(fill="x", padx=10, pady=10)
    
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
            messagebox.showerror("Error", f"Failed to load customers: {e}")
    
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
                    f"${product['price_normal']:.2f}",
                    f"${product['price_workshop']:.2f}"
                ))
            
            self.all_products = products
            
        except Exception as e:
            print(f"Error loading products: {e}")
            messagebox.showerror("Error", f"Failed to load products: {e}")
    
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
                    f"${product['price_normal']:.2f}",
                    f"${product['price_workshop']:.2f}"
                ))
    
    def on_customer_selected(self, customer_name):
        """Handle customer selection"""
        self.current_customer = self.customers_data.get(customer_name)
        self.update_cart_display()
    
    def add_to_cart(self):
        """Add selected product to cart"""
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
        quantity_dialog = QuantityDialog(self.parent, product['stock'])
        quantity = quantity_dialog.get_quantity()
        
        if quantity and quantity > 0:
            if quantity > product['stock']:
                messagebox.showerror("Error", "Insufficient stock available.")
                return
            
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
                    messagebox.showerror("Error", "Total quantity would exceed stock.")
                    return
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
                f"${unit_price:.2f}",
                f"${total_price:.2f}"
            ))
        
        # Update totals
        self.subtotal_label.configure(text=f"Subtotal: ${subtotal:.2f}")
        self.total_label.configure(text=f"Total: ${subtotal:.2f}")
    
    def process_sale(self):
        """Process the sale transaction"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        try:
            # Generate invoice number
            invoice_number = self.generate_invoice_number()
            
            # Calculate totals
            customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
            subtotal = 0
            
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                subtotal += unit_price * item['quantity']
            
            # Create sale record
            customer_id = self.current_customer['customer_id'] if self.current_customer else None
            payment_method = self.payment_var.get().lower()
            
            sale_id = db.execute_insert("""
                INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method,
                                 subtotal, total_amount, paid_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_number,
                customer_id,
                datetime.now().date(),
                payment_method,
                subtotal,
                subtotal,
                subtotal if payment_method == 'cash' else 0,
                'completed'
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
                
                # Update stock and qty_sold
                db.execute_update("""
                    UPDATE products 
                    SET stock = stock - ?, 
                        qty_sold = qty_sold + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                """, (item['quantity'], item['quantity'], item['product_id']))
                
                # Record stock movement
                db.execute_insert("""
                    INSERT INTO stock_movements 
                    (product_id, movement_type, quantity, reference_id, reference_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item['product_id'],
                    'sale',
                    -item['quantity'],
                    sale_id,
                    'sale'
                ))
            
            # Update customer credit balance if needed
            if payment_method == 'credit' and customer_id:
                db.execute_update("""
                    UPDATE customers 
                    SET credit_balance = credit_balance + ?
                    WHERE customer_id = ?
                """, (subtotal, customer_id))
            
            # Generate and show invoice
            self.generate_invoice(sale_id, invoice_number)
            
            # Clear cart and refresh
            self.cart_items = []
            self.update_cart_display()
            self.load_products()
            
            messagebox.showinfo("Success", f"Sale completed successfully!\nInvoice: {invoice_number}")
            
        except Exception as e:
            print(f"Error processing sale: {e}")
            messagebox.showerror("Error", f"Failed to process sale: {e}")
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        today = datetime.now()
        base_number = f"INV-{today.strftime('%Y%m%d')}"
        
        # Find next number for today
        query = "SELECT COUNT(*) as count FROM sales WHERE invoice_number LIKE ?"
        result = db.execute_query(query, (f"{base_number}-%",))
        count = result[0]['count'] if result else 0
        
        return f"{base_number}-{count + 1:03d}"
    
    def generate_invoice(self, sale_id, invoice_number):
        """Generate PDF invoice"""
        try:
            # Get sale details
            sale_query = """
                SELECT s.*, c.name as customer_name, c.type as customer_type
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.id = ?
            """
            sale_data = db.execute_query(sale_query, (sale_id,))[0]
            
            # Get sale items
            items_query = """
                SELECT si.*, p.name as product_name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
            """
            items_data = db.execute_query(items_query, (sale_id,))
            
            # Create PDF
            filename = f"reports/invoice_{invoice_number}.pdf"
            os.makedirs("reports", exist_ok=True)
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            story.append(Paragraph("<b>INVENTORY PRO</b>", styles['Title']))
            story.append(Paragraph("Sales Invoice", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Invoice details
            invoice_info = [
                ["Invoice Number:", invoice_number],
                ["Date:", sale_data['sale_date']],
                ["Customer:", sale_data['customer_name'] or 'Walk-in Customer'],
                ["Payment Method:", sale_data['payment_method'].title()]
            ]
            
            info_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Items table
            items_table_data = [["SKU", "Product", "Qty", "Price", "Total"]]
            
            for item in items_data:
                items_table_data.append([
                    item['sku'],
                    item['product_name'],
                    str(item['quantity']),
                    f"${item['unit_price']:.2f}",
                    f"${item['total']:.2f}"
                ])
            
            # Add totals
            items_table_data.append(["", "", "", "Subtotal:", f"${sale_data['subtotal']:.2f}"])
            items_table_data.append(["", "", "", "<b>Total:</b>", f"<b>${sale_data['total_amount']:.2f}</b>"])
            
            items_table = Table(items_table_data, colWidths=[1*inch, 2.5*inch, 0.7*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -3), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 30))
            
            # Footer
            story.append(Paragraph("Thank you for your business!", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Ask if user wants to open the PDF
            if messagebox.askyesno("Invoice Generated", f"Invoice saved as {filename}\n\nWould you like to open it?"):
                os.startfile(filename)
            
        except Exception as e:
            print(f"Error generating invoice: {e}")
            messagebox.showerror("Error", f"Failed to generate invoice: {e}")


class QuantityDialog:
    def __init__(self, parent, max_quantity):
        self.parent = parent
        self.max_quantity = max_quantity
        self.quantity = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Enter Quantity")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Focus on entry
        self.quantity_entry.focus()
    
    def create_widgets(self):
        # Label
        label = ctk.CTkLabel(
            self.dialog, 
            text=f"Enter quantity (Max: {self.max_quantity}):",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=20)
        
        # Entry
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ctk.CTkEntry(
            self.dialog,
            textvariable=self.quantity_var,
            width=100,
            justify="center"
        )
        self.quantity_entry.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=10)
        
        ok_button = ctk.CTkButton(
            button_frame,
            text="OK",
            command=self.ok_clicked,
            width=80
        )
        ok_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_clicked,
            width=80
        )
        cancel_button.pack(side="left", padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
    
    def ok_clicked(self):
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            if quantity > self.max_quantity:
                messagebox.showerror("Error", f"Quantity cannot exceed {self.max_quantity}")
                return
            
            self.quantity = quantity
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def cancel_clicked(self):
        self.dialog.destroy()
    
    def get_quantity(self):
        self.dialog.wait_window()
        return self.quantity
