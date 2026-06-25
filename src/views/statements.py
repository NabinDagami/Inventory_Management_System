import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
import utils.simple_table_styles as table_styles
from utils.format_utils import format_price_with_decimals
from utils.dialog_utils import size_and_center_dialog

class StatementsView:
    def __init__(self, parent):
        self.parent = parent
        self.current_tab = "sales"
        self.create_statements_interface()
        self.load_data()
    
    def format_price(self, price):
        """Format price with comma separators like inventory"""
        return format_price_with_decimals(price)
    
    def create_statements_interface(self):
        """Create the statements management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame)
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.sales_btn = ctk.CTkButton(
            tab_frame,
            text="💰 Sales Records",
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("sales")
        )
        self.sales_btn.pack(side="left", padx=(0, 10))
        
        self.credit_btn = ctk.CTkButton(
            tab_frame,
            text="💳 Credit Records",
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("credit")
        )
        self.credit_btn.pack(side="left", padx=(0, 10))
        
        self.payment_btn = ctk.CTkButton(
            tab_frame,
            text="💵 Payment Records",
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("payment")
        )
        self.payment_btn.pack(side="left")
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        search_label = ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search records by invoice, customer, date...",
            width=250
        )
        search_entry.pack(side="left", padx=5, pady=10)
        
        # Content area with table
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create table
        self.create_table(content_frame)
    
    def create_table(self, parent):
        """Create the data table"""
        # Table frame
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create columns based on tab
        columns = ("Invoice #", "Date", "Customer", "Amount", "Paid", "Balance", "Status")
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_sales_history_style(self.data_tree)
        
        # Define headings and column widths
        column_widths = {"Invoice #": 140, "Date": 120, "Customer": 200, 
                        "Amount": 120, "Paid": 120, "Balance": 120, "Status": 100}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center", minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        v_scrollbar.pack(side="right", fill="y", pady=5)
        h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        # Bind double-click to view details
        self.data_tree.bind("<Double-1>", lambda e: self.view_details())
    
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
        inactive_text_color = ("gray10", "gray90")
        
        if tab_name == "sales":
            self.sales_btn.configure(fg_color=active_color, text_color="white")
            self.credit_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.payment_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        elif tab_name == "credit":
            self.sales_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_btn.configure(fg_color=active_color, text_color="white")
            self.payment_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        else:  # payment
            self.sales_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.payment_btn.configure(fg_color=active_color, text_color="white")
        
        # Clear search and reload data
        self.search_var.set("")
        self.load_data()
    
    def load_data(self):
        """Load data for current tab"""
        try:
            # Clear existing items
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            if self.current_tab == "sales":
                self.load_sales_data()
            elif self.current_tab == "credit":
                self.load_credit_data()
            elif self.current_tab == "payment":
                self.load_payment_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def load_sales_data(self):
        """Load all sales records"""
        query = """
            SELECT s.invoice_number, s.sale_date, c.name as customer_name,
                   s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as balance,
                   s.status
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            ORDER BY s.sale_date DESC, s.id DESC
        """
        sales = db.execute_query(query)
        self.all_data = sales
        
        for sale in sales:
            customer_name = sale['customer_name'] or "Walk-in Customer"
            balance = sale['balance'] if sale['balance'] else 0
            
            # Determine status color
            status = sale['status'].title()
            
            self.data_tree.insert("", "end", values=(
                sale['invoice_number'],
                sale['sale_date'],
                customer_name,
                format_price_with_decimals(sale['total_amount']),
                format_price_with_decimals(sale['paid_amount']),
                format_price_with_decimals(balance),
                status
            ))
    
    def load_credit_data(self):
        """Load credit sales records"""
        query = """
            SELECT s.invoice_number, s.sale_date, c.name as customer_name,
                   s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as balance,
                   s.status
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.status = 'credit' AND (s.total_amount - s.paid_amount) > 0
            ORDER BY s.sale_date DESC, s.id DESC
        """
        credits = db.execute_query(query)
        self.all_data = credits
        
        for credit in credits:
            customer_name = credit['customer_name'] or "Walk-in Customer"
            balance = credit['balance'] if credit['balance'] else 0
            
            self.data_tree.insert("", "end", values=(
                credit['invoice_number'],
                credit['sale_date'],
                customer_name,
                format_price_with_decimals(credit['total_amount']),
                format_price_with_decimals(credit['paid_amount']),
                format_price_with_decimals(balance),
                "Credit"
            ))
    
    def load_payment_data(self):
        """Load payment records"""
        query = """
            SELECT s.invoice_number, s.sale_date, c.name as customer_name,
                   s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as balance,
                   s.payment_method
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.paid_amount > 0
            ORDER BY s.sale_date DESC, s.id DESC
        """
        payments = db.execute_query(query)
        self.all_data = payments
        
        for payment in payments:
            customer_name = payment['customer_name'] or "Walk-in Customer"
            balance = payment['balance'] if payment['balance'] else 0
            
            self.data_tree.insert("", "end", values=(
                payment['invoice_number'],
                payment['sale_date'],
                customer_name,
                format_price_with_decimals(payment['total_amount']),
                format_price_with_decimals(payment['paid_amount']),
                format_price_with_decimals(balance),
                payment['payment_method'].title()
            ))
    
    def filter_data(self, *args):
        """Filter data based on search"""
        search_term = self.search_var.get().lower()
        
        # Clear tree
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not hasattr(self, 'all_data'):
            return
        
        # Filter and display matching items
        for item in self.all_data:
            customer_name = item['customer_name'] or "Walk-in Customer"
            
            if (search_term in item['invoice_number'].lower() or
                search_term in customer_name.lower() or
                search_term in str(item['sale_date']).lower()):
                
                balance = item['balance'] if item['balance'] else 0
                
                if self.current_tab == "payment":
                    # Get payment_method if exists, otherwise use status
                    if 'payment_method' in item.keys() and item['payment_method']:
                        status = item['payment_method'].title()
                    else:
                        status = "Payment"
                else:
                    status = item['status'].title() if 'status' in item.keys() else "Credit"
                
                self.data_tree.insert("", "end", values=(
                    item['invoice_number'],
                    item['sale_date'],
                    customer_name,
                    format_price_with_decimals(item['total_amount']),
                    format_price_with_decimals(item['paid_amount']),
                    format_price_with_decimals(balance),
                    status
                ))
    
    def view_details(self):
        """View record details in a dialog"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to view details.")
            return
        
        item_values = self.data_tree.item(selection[0], 'values')
        invoice_number = item_values[0]
        
        try:
            # Get detailed sale information
            query = """
                SELECT s.*, c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.invoice_number = ?
            """
            result = db.execute_query(query, (invoice_number,))
            
            if not result:
                messagebox.showerror("Error", "Record not found.")
                return
            
            sale = result[0]
            
            # Create detail dialog
            self.create_detail_dialog(sale, invoice_number)
            
        except Exception as e:
            print(f"Error loading record details: {e}")
            messagebox.showerror("Error", f"Failed to load record details: {e}")
    
    def create_detail_dialog(self, sale, invoice_number):
        """Create a detailed view dialog for the selected record"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Record Details - {invoice_number}")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(True, True)
        size_and_center_dialog(dialog, self.parent, 600, 700, min_w=480, min_h=500)
        
        # Title (fixed header)
        title_label = ctk.CTkLabel(
            dialog,
            text=f"📋 {self.current_tab.title()} Record Details",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Scrollable content
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(5, 0))
        
        # Invoice Info Section
        invoice_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
        invoice_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(
            invoice_frame,
            text="🧾 Invoice Information",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.create_info_row(invoice_frame, "Invoice Number:", sale['invoice_number'])
        self.create_info_row(invoice_frame, "Date:", sale['sale_date'])
        self.create_info_row(invoice_frame, "Status:", sale['status'].title())
        self.create_info_row(invoice_frame, "Payment Method:", sale['payment_method'].title() if sale['payment_method'] else "N/A")
        
        # Customer Info Section
        customer_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
        customer_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(
            customer_frame,
            text="👤 Customer Information",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        customer_name = sale['customer_name'] or "Walk-in Customer"
        self.create_info_row(customer_frame, "Name:", customer_name)
        
        # Financial Info Section
        financial_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
        financial_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(
            financial_frame,
            text="💰 Financial Information",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        total_amount = sale['total_amount'] or 0
        paid_amount = sale['paid_amount'] or 0
        balance = total_amount - paid_amount
        
        self.create_info_row(financial_frame, "Total Amount:", format_price_with_decimals(total_amount), color="#10B981")
        self.create_info_row(financial_frame, "Paid Amount:", format_price_with_decimals(paid_amount), color="#3B82F6")
        
        # Show balance with color coding
        if balance > 0:
            balance_color = "#EF4444"  # Red for outstanding
        else:
            balance_color = "#10B981"  # Green for paid
        
        self.create_info_row(financial_frame, "Balance:", format_price_with_decimals(balance), color=balance_color)
        
        # Notes Section (if available)
        if 'notes' in sale.keys() and sale['notes']:
            notes_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
            notes_frame.pack(fill="x", pady=(0, 15), padx=5)
            
            ctk.CTkLabel(
                notes_frame,
                text="📝 Notes",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            notes_text = ctk.CTkTextbox(notes_frame, height=80, wrap="word")
            notes_text.pack(fill="x", padx=15, pady=(0, 10))
            notes_text.insert("1.0", sale['notes'])
            notes_text.configure(state="disabled")
        
        # Close button (fixed footer)
        close_btn = ctk.CTkButton(
            dialog,
            text="❌ Close",
            command=dialog.destroy,
            width=150,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        close_btn.pack(pady=(10, 15))
    
    def create_info_row(self, parent, label, value, color=None):
        """Create a label-value row for the detail dialog"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=3)
        
        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            row,
            text=str(value),
            font=ctk.CTkFont(size=12),
            text_color=color if color else ("gray10", "gray90"),
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)
