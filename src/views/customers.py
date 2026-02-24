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
from views.payment_dialog import PaymentDialog
from utils.export_manager import ExportManager
from utils.format_utils import format_price_with_decimals, get_currency_symbol

class CustomersView:
    def __init__(self, parent):
        self.parent = parent
        self.create_customers_interface()
        self.load_customers()
    
    def create_customers_interface(self):
        """Create the customers management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Customer Management",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Add Customer Button
        add_customer_btn = ctk.CTkButton(
            header_frame,
            text="➕ Add Customer",
            command=self.add_customer,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        add_customer_btn.pack(side="right", padx=10, pady=10)
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Row 1: Search and main filters
        row1_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Search
        search_label = ctk.CTkLabel(row1_frame, text="🔍 Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_customers)
        search_entry = ctk.CTkEntry(
            row1_frame,
            textvariable=self.search_var,
            placeholder_text="Search by name, contact, or type...",
            width=280
        )
        search_entry.pack(side="left", padx=5)
        
        # Customer type filter
        type_label = ctk.CTkLabel(row1_frame, text="Type:", font=ctk.CTkFont(size=12, weight="bold"))
        type_label.pack(side="left", padx=(15, 5))
        
        self.type_filter_var = tk.StringVar(value="All")
        type_filter = ctk.CTkOptionMenu(
            row1_frame,
            variable=self.type_filter_var,
            values=["All", "Normal", "Workshop"],
            command=self.filter_customers,
            width=110
        )
        type_filter.pack(side="left", padx=5)
        
        # Row 2: Advanced filters and actions
        row2_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row2_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Status filter
        status_label = ctk.CTkLabel(row2_frame, text="Status:", font=ctk.CTkFont(size=12, weight="bold"))
        status_label.pack(side="left", padx=(0, 5))
        
        self.status_filter_var = tk.StringVar(value="All")
        status_filter = ctk.CTkOptionMenu(
            row2_frame,
            variable=self.status_filter_var,
            values=["All", "Active", "Inactive"],
            command=self.filter_customers,
            width=110
        )
        status_filter.pack(side="left", padx=5)
        
        # Credit filter
        credit_label = ctk.CTkLabel(row2_frame, text="Credit:", font=ctk.CTkFont(size=12, weight="bold"))
        credit_label.pack(side="left", padx=(15, 5))
        
        self.credit_filter_var = tk.StringVar(value="All")
        credit_filter = ctk.CTkOptionMenu(
            row2_frame,
            variable=self.credit_filter_var,
            values=["All", "Has Credit", "No Credit"],
            command=self.filter_customers,
            width=120
        )
        credit_filter.pack(side="left", padx=5)
        
        # Clear filters button
        clear_btn = ctk.CTkButton(
            row2_frame,
            text="❌ Clear Filters",
            command=self.clear_filters,
            width=120,
            height=32,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_btn.pack(side="left", padx=(15, 5))
        
        # Export buttons frame
        export_frame = ctk.CTkFrame(row2_frame)
        export_frame.pack(side="right")
        
        export_excel_btn = ctk.CTkButton(
            export_frame,
            text="📊 Excel",
            width=80,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_to_excel,
            fg_color="#10B981",
            hover_color="#059669"
        )
        export_excel_btn.pack(side="left", padx=(0, 5))
        
        export_pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 PDF",
            width=80,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_to_pdf,
            fg_color="#F59E0B",
            hover_color="#D97706"
        )
        export_pdf_btn.pack(side="left")
        
        # Action buttons — packed BEFORE table so they are always visible
        actions_frame = ctk.CTkFrame(main_frame)
        actions_frame.pack(fill="x", padx=10, pady=(0, 5), side="bottom")

        # Customers table
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Create treeview for customers with enhanced styling
        columns = ("ID", "Name", "Type", "Contact", "Credit Balance", "Status", "Created")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Apply centralized styling
        table_styles.apply_customer_style(self.customers_tree)
        
        # Define headings and column widths
        column_widths = {"ID": 80, "Name": 220, "Type": 100, "Contact": 240,
                        "Credit Balance": 140, "Status": 100, "Created": 120}
        
        for col in columns:
            self.customers_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.customers_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col in ["ID", "Type", "Credit Balance", "Status"] else "w", minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.customers_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.customers_tree.xview)
        self.customers_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.customers_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        v_scrollbar.pack(side="right", fill="y", pady=5)
        h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit Customer",
            command=self.edit_customer,
            width=120,
            height=35
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete Customer",
            command=self.delete_customer,
            width=130,
            height=35,
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="left", padx=5)
        
        toggle_status_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Toggle Status",
            command=self.toggle_customer_status,
            width=120,
            height=35
        )
        toggle_status_btn.pack(side="left", padx=5)
        
        # Record Payment button
        payment_btn = ctk.CTkButton(
            actions_frame,
            text="💰 Record Payment",
            command=self.record_payment,
            width=140,
            height=35,
            fg_color="#4caf50",
            hover_color="#45a049"
        )
        payment_btn.pack(side="left", padx=5)

        # Customer Statement button
        statement_btn = ctk.CTkButton(
            actions_frame,
            text="📄 Statement",
            command=self.view_customer_statement,
            width=120,
            height=35,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        statement_btn.pack(side="left", padx=5)

        # Double-click to edit
        self.customers_tree.bind("<Double-1>", lambda e: self.edit_customer())
    
    def load_customers(self):
        """Load customers data"""
        try:
            query = """
                SELECT customer_id, name, type, contact, credit_balance, is_active, 
                       DATE(created_at) as created_date
                FROM customers
                ORDER BY name
            """
            customers = db.execute_query(query)
            
            # Clear existing items
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            
            # Add customers to tree
            for customer in customers:
                status = "Active" if customer['is_active'] else "Inactive"
                credit_balance = format_price_with_decimals(customer['credit_balance'])
                
                self.customers_tree.insert("", "end", values=(
                    customer['customer_id'],
                    customer['name'],
                    customer['type'],
                    customer['contact'] or "N/A",
                    credit_balance,
                    status,
                    customer['created_date']
                ))
            
            self.all_customers = customers
            
        except Exception as e:
            print(f"Error loading customers: {e}")
            messagebox.showerror("Error", f"Failed to load customers: {e}")
    
    def filter_customers(self, *args):
        """Filter customers based on search and type filter"""
        if not hasattr(self, 'all_customers'):
            return
            
        search_term = self.search_var.get().lower()
        type_filter = self.type_filter_var.get()
        status_filter = self.status_filter_var.get()
        credit_filter = self.credit_filter_var.get()
        
        # Clear tree
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Filter and add matching customers
        for customer in self.all_customers:
            # Check search term
            matches_search = (
                search_term in customer['name'].lower() or
                search_term in customer['type'].lower() or
                search_term in (customer['contact'] or "").lower()
            )
            
            # Check type filter
            matches_type = type_filter == "All" or customer['type'] == type_filter
            
            # Check status filter
            customer_status = "Active" if customer['is_active'] else "Inactive"
            matches_status = status_filter == "All" or customer_status == status_filter
            
            # Check credit filter
            has_credit = customer['credit_balance'] > 0
            if credit_filter == "All":
                matches_credit = True
            elif credit_filter == "Has Credit":
                matches_credit = has_credit
            else:  # No Credit
                matches_credit = not has_credit
            
            if matches_search and matches_type and matches_status and matches_credit:
                credit_balance = format_price_with_decimals(customer['credit_balance'])
                
                self.customers_tree.insert("", "end", values=(
                    customer['customer_id'],
                    customer['name'],
                    customer['type'],
                    customer['contact'] or "N/A",
                    credit_balance,
                    customer_status,
                    customer['created_date']
                ))
    
    def clear_filters(self):
        """Clear all filters and reload data"""
        self.search_var.set("")
        self.type_filter_var.set("All")
        self.status_filter_var.set("All")
        self.credit_filter_var.set("All")
        self.filter_customers()
    
    def export_to_excel(self):
        """Export customers to Excel"""
        ExportManager.export_customers_to_excel()
    
    def export_to_pdf(self):
        """Export customers to PDF"""
        ExportManager.export_customers_to_pdf()
    
    def add_customer(self):
        """Add a new customer"""
        dialog = CustomerDialog(self.parent, title="Add Customer")
        if dialog.result:
            self.load_customers()
    
    def edit_customer(self):
        """Edit selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to edit.")
            return
        
        customer_id = self.customers_tree.item(selection[0], 'values')[0]
        
        # Get customer data
        customer = db.execute_query(
            "SELECT * FROM customers WHERE customer_id = ?", 
            (customer_id,)
        )
        
        if customer:
            dialog = CustomerDialog(self.parent, title="Edit Customer", customer_data=customer[0])
            if dialog.result:
                self.load_customers()
    
    def delete_customer(self):
        """Delete selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to delete.")
            return
        
        customer_id = self.customers_tree.item(selection[0], 'values')[0]
        customer_name = self.customers_tree.item(selection[0], 'values')[1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{customer_name}'?"):
            try:
                db.execute_update(
                    "DELETE FROM customers WHERE customer_id = ?", 
                    (customer_id,)
                )
                messagebox.showinfo("Success", "Customer deleted successfully!")
                self.load_customers()
            except Exception as e:
                print(f"Error deleting customer: {e}")
                messagebox.showerror("Error", f"Failed to delete customer: {e}")
    
    def toggle_customer_status(self):
        """Toggle customer active/inactive status"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to toggle status.")
            return
        
        customer_id = self.customers_tree.item(selection[0], 'values')[0]
        customer_name = self.customers_tree.item(selection[0], 'values')[1]
        current_status = self.customers_tree.item(selection[0], 'values')[5]
        
        new_status = 0 if current_status == "Active" else 1
        status_text = "activate" if new_status else "deactivate"
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to {status_text} customer '{customer_name}'?"):
            try:
                db.execute_update(
                    "UPDATE customers SET is_active = ? WHERE customer_id = ?", 
                    (new_status, customer_id)
                )
                messagebox.showinfo("Success", f"Customer {status_text}d successfully!")
                self.load_customers()
            except Exception as e:
                print(f"Error updating customer status: {e}")
                messagebox.showerror("Error", f"Failed to update customer status: {e}")
    
    def view_customer_statement(self):
        """Show full sales + payment history for selected customer."""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to view statement.")
            return

        customer_id = self.customers_tree.item(selection[0], 'values')[0]
        customer = db.execute_query("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        if customer:
            CustomerStatementDialog(self.parent, customer[0])

    def record_payment(self):
        """Record payment for selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to record payment.")
            return
        
        customer_id = self.customers_tree.item(selection[0], 'values')[0]
        
        # Get current customer data
        customer = db.execute_query(
            "SELECT * FROM customers WHERE customer_id = ?", 
            (customer_id,)
        )
        
        if customer:
            customer_data = customer[0]
            
            # Check if customer has any credit balance
            if customer_data['credit_balance'] <= 0:
                if not messagebox.askyesno("No Credit Balance", 
                    f"Customer '{customer_data['name']}' has no outstanding credit balance.\n"
                    "Do you still want to record a payment? This will create a credit balance for the customer."):
                    return
            
            dialog = PaymentDialog(
                self.parent, 
                payment_type="customer", 
                customer_data=customer_data
            )
            
            if dialog.result:
                self.load_customers()  # Refresh the customer list


class CustomerDialog:
    def __init__(self, parent, title="Customer Dialog", customer_data=None):
        self.parent = parent
        self.customer_data = customer_data
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("580x750")  # Further increased height to show all elements
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)  # Allow resizing so user can adjust if needed
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_form()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self):
        """Create customer form with modern styling"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with icon
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#e8eaf6", "#3f51b5"))
        header_frame.pack(fill="x", padx=15, pady=(15, 20))
        
        customer_icon = ctk.CTkLabel(header_frame, text="👥", font=ctk.CTkFont(size=28))
        customer_icon.pack(pady=(15, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Customer Information",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1a237e", "white")
        )
        header_label.pack(pady=(0, 15))
        
        # Form fields container
        fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=15)
        
        # Customer Name
        name_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        name_frame.pack(fill="x", pady=(0, 12))
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="📝 Customer Name *:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter customer name...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Customer Type
        type_frame_container = ctk.CTkFrame(fields_frame, corner_radius=10)
        type_frame_container.pack(fill="x", pady=(0, 12))
        
        type_label = ctk.CTkLabel(
            type_frame_container,
            text="🏷️ Customer Type:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        type_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.type_var = tk.StringVar(value="Normal")
        type_radio_frame = ctk.CTkFrame(type_frame_container, fg_color="transparent")
        type_radio_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        normal_radio = ctk.CTkRadioButton(
            type_radio_frame, 
            text="👤 Normal Customer", 
            variable=self.type_var, 
            value="Normal",
            font=ctk.CTkFont(size=12)
        )
        normal_radio.pack(side="left", padx=(0, 30))
        
        workshop_radio = ctk.CTkRadioButton(
            type_radio_frame, 
            text="🔧 Workshop Customer", 
            variable=self.type_var, 
            value="Workshop",
            font=ctk.CTkFont(size=12)
        )
        workshop_radio.pack(side="left")
        
        # Contact Information
        contact_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        contact_frame.pack(fill="x", pady=(0, 12))
        
        contact_label = ctk.CTkLabel(
            contact_frame,
            text="📞 Contact Information:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        contact_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.contact_text = ctk.CTkTextbox(
            contact_frame, 
            height=70, 
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.contact_text.pack(fill="x", padx=15, pady=(0, 12))
        
        # Credit Balance
        credit_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        credit_frame.pack(fill="x", pady=(0, 12))
        
        credit_label = ctk.CTkLabel(
            credit_frame,
            text=f"💳 Credit Balance ({get_currency_symbol()}):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        credit_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.credit_entry = ctk.CTkEntry(
            credit_frame,
            placeholder_text="0.00",
            font=ctk.CTkFont(size=13),
            height=35,
            width=150
        )
        self.credit_entry.pack(anchor="w", padx=15, pady=(0, 12))
        
        # Active Status
        status_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 15))
        
        self.active_var = tk.BooleanVar(value=True)
        active_checkbox = ctk.CTkCheckBox(
            status_frame, 
            text="✅ Active Customer", 
            variable=self.active_var,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        active_checkbox.pack(anchor="w", padx=15, pady=12)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(10, 15))
        
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
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Customer",
            command=self.save_customer,
            width=150,
            height=45,
            corner_radius=10,
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="right")
        
        # Focus on name entry
        self.name_entry.focus()
        
        # Fill form if editing
        if self.customer_data:
            self.fill_form()
    
    def fill_form(self):
        """Fill form with existing customer data"""
        self.name_entry.insert(0, self.customer_data['name'])
        self.type_var.set(self.customer_data['type'])
        if self.customer_data['contact']:
            self.contact_text.insert("1.0", self.customer_data['contact'])
        self.credit_entry.insert(0, str(self.customer_data['credit_balance']))
        self.active_var.set(bool(self.customer_data['is_active']))
    
    def save_customer(self):
        """Save customer data"""
        # Validate required fields
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "Customer name is required!")
            return
        
        try:
            # Get form data
            name = self.name_entry.get().strip()
            customer_type = self.type_var.get()
            contact = self.contact_text.get("1.0", "end-1c").strip()
            credit_balance = float(self.credit_entry.get() or 0)
            is_active = self.active_var.get()
            
            if self.customer_data:  # Edit existing customer
                db.execute_update(
                    """UPDATE customers SET name = ?, type = ?, contact = ?, 
                       credit_balance = ?, is_active = ? WHERE customer_id = ?""",
                    (name, customer_type, contact, credit_balance, is_active, 
                     self.customer_data['customer_id'])
                )
                messagebox.showinfo("Success", "Customer updated successfully!")
            else:  # Add new customer
                db.execute_insert(
                    """INSERT INTO customers (name, type, contact, credit_balance, is_active) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, customer_type, contact, credit_balance, is_active)
                )
                messagebox.showinfo("Success", "Customer added successfully!")
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid credit balance amount.")
        except Exception as e:
            print(f"Error saving customer: {e}")
            messagebox.showerror("Error", f"Failed to save customer: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = False
        self.dialog.destroy()


class CustomerStatementDialog:
    """Shows a full statement: all sales + credit payments for a customer."""

    def __init__(self, parent, customer_data):
        self.parent = parent
        self.customer = customer_data

        self.dialog = ctk.CTkToplevel(parent)
        title_text = "Statement - " + customer_data['name']
        self.dialog.title(title_text)
        self.dialog.geometry("820x620")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        x = parent.winfo_rootx() + 40
        y = parent.winfo_rooty() + 40
        self.dialog.geometry("+%d+%d" % (x, y))

        self._build_ui()
        self._load_data()
        self.dialog.wait_window()

    def _build_ui(self):
        main = ctk.CTkScrollableFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Customer info header
        info_frame = ctk.CTkFrame(main, fg_color=("#dbeafe", "#1e3a5f"))
        info_frame.pack(fill="x", pady=(0, 10))

        name_text = "Customer: " + self.customer['name'] + "  |  Type: " + self.customer['type']
        ctk.CTkLabel(
            info_frame,
            text=name_text,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=15, pady=10)

        balance_text = "Outstanding Credit: " + format_price_with_decimals(self.customer['credit_balance'])
        self.balance_label = ctk.CTkLabel(
            info_frame,
            text=balance_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.balance_label.pack(side="right", padx=15, pady=10)

        # Sales section header
        ctk.CTkLabel(
            main,
            text="Sales History",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(5, 3))

        sales_frame = ctk.CTkFrame(main)
        sales_frame.pack(fill="x", pady=(0, 10))
        sales_frame.grid_columnconfigure(0, weight=1)

        sale_cols = ("Invoice", "Date", "Total", "Paid", "Balance", "Status")
        self.sales_tree = ttk.Treeview(
            sales_frame, columns=sale_cols, show="headings", height=8
        )
        sale_widths = {
            "Invoice": 160, "Date": 100, "Total": 110,
            "Paid": 110, "Balance": 110, "Status": 90
        }
        for col in sale_cols:
            self.sales_tree.heading(col, text=col, anchor="center")
            self.sales_tree.column(
                col, width=sale_widths.get(col, 100), anchor="center", minwidth=70
            )

        s_vsb = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=s_vsb.set)
        self.sales_tree.grid(row=0, column=0, sticky="ew")
        s_vsb.grid(row=0, column=1, sticky="ns")

        self.sales_summary = ctk.CTkLabel(
            main, text="", font=ctk.CTkFont(size=12), text_color="#FF6B35"
        )
        self.sales_summary.pack(anchor="e", padx=5, pady=(0, 8))

        # Payments section header
        ctk.CTkLabel(
            main,
            text="Credit Payment History",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(5, 3))

        pay_frame = ctk.CTkFrame(main)
        pay_frame.pack(fill="x", pady=(0, 10))
        pay_frame.grid_columnconfigure(0, weight=1)

        pay_cols = ("Date", "Invoice", "Amount Paid", "Remaining After", "Recorded At")
        self.pay_tree = ttk.Treeview(
            pay_frame, columns=pay_cols, show="headings", height=6
        )
        pay_widths = {
            "Date": 100, "Invoice": 160, "Amount Paid": 120,
            "Remaining After": 130, "Recorded At": 160
        }
        for col in pay_cols:
            self.pay_tree.heading(col, text=col, anchor="center")
            self.pay_tree.column(
                col, width=pay_widths.get(col, 110), anchor="center", minwidth=70
            )

        p_vsb = ttk.Scrollbar(pay_frame, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=p_vsb.set)
        self.pay_tree.grid(row=0, column=0, sticky="ew")
        p_vsb.grid(row=0, column=1, sticky="ns")

        ctk.CTkButton(
            main,
            text="Close",
            command=self.dialog.destroy,
            width=100,
            height=35,
            fg_color="#6B7280",
            hover_color="#4B5563"
        ).pack(pady=10)

    def _load_data(self):
        cid = self.customer['customer_id']

        # Load sales
        try:
            sales = db.execute_query(
                "SELECT invoice_number, sale_date, total_amount, paid_amount,"
                " (total_amount - paid_amount) as balance, status"
                " FROM sales WHERE customer_id = ?"
                " ORDER BY sale_date DESC, id DESC",
                (cid,)
            )
            total_billed = 0
            total_paid = 0
            total_balance = 0
            for s in sales:
                self.sales_tree.insert("", "end", values=(
                    s['invoice_number'],
                    s['sale_date'],
                    format_price_with_decimals(s['total_amount']),
                    format_price_with_decimals(s['paid_amount']),
                    format_price_with_decimals(s['balance']),
                    s['status'].title()
                ))
                total_billed += s['total_amount']
                total_paid += s['paid_amount']
                total_balance += s['balance']

            summary = (
                f"Total Billed: {format_price_with_decimals(total_billed)}  |  "
                f"Total Paid: {format_price_with_decimals(total_paid)}  |  "
                f"Outstanding: {format_price_with_decimals(total_balance)}"
            )
            self.sales_summary.configure(text=summary)
        except Exception as e:
            print("Error loading sales for statement:", e)

        # Load payments
        try:
            payments = db.execute_query(
                "SELECT p.payment_date, s.invoice_number, p.amount, p.notes, p.created_at"
                " FROM payments p"
                " LEFT JOIN sales s ON p.reference_number = s.invoice_number"
                " WHERE p.customer_id = ? AND p.payment_type = 'credit_sale'"
                " ORDER BY p.created_at DESC",
                (cid,)
            )
            for p in payments:
                remaining = "-"
                try:
                    if p['notes'] and p['notes'].startswith("remaining:"):
                        remaining = format_price_with_decimals(float(p['notes'].split(':')[1]))
                except Exception:
                    pass
                self.pay_tree.insert("", "end", values=(
                    p['payment_date'],
                    p['invoice_number'] or "-",
                    format_price_with_decimals(p['amount']),
                    remaining,
                    p['created_at']
                ))
        except Exception as e:
            print("Error loading payments for statement:", e)
