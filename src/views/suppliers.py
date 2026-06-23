import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
import utils.simple_table_styles as table_styles
from utils.export_manager import ExportManager
from utils.dialog_utils import size_and_center_dialog

class SuppliersView:
    def __init__(self, parent):
        self.parent = parent
        self.create_suppliers_view()
        self.load_data()
    
    def create_suppliers_view(self):
        """Create suppliers management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with action buttons
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🏦 Supplier Management", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Action buttons
        action_frame = ctk.CTkFrame(header_frame)
        action_frame.pack(side="right", padx=10, pady=10)
        
        self.add_btn = ctk.CTkButton(
            action_frame,
            text="➕ Add Supplier",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.add_supplier,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.add_btn.pack(side="left", padx=(0, 5))
        
        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Edit",
            width=80,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.edit_supplier
        )
        self.edit_btn.pack(side="left", padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Delete",
            width=80,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.delete_supplier,
            fg_color="red",
            hover_color="darkred"
        )
        self.delete_btn.pack(side="left")
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Row 1: Search
        row1_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        search_label = ctk.CTkLabel(row1_frame, text="🔍 Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_data)
        search_entry = ctk.CTkEntry(
            row1_frame,
            textvariable=self.search_var,
            placeholder_text="Search by name, contact person, email, or phone...",
            width=400
        )
        search_entry.pack(side="left", padx=5)
        
        # Row 2: Filters and actions
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
            command=self.filter_data,
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
            command=self.filter_data,
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
        
        # Content area with table
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create table
        self.create_table(content_frame)
    
    def create_table(self, parent):
        """Create the suppliers table"""
        # Table frame
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for suppliers with enhanced styling
        columns = ("ID", "Name", "Contact Person", "Email", "Phone", "Address", "Credit Balance", "Status")
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_supplier_style(self.data_tree)
        
        # Define headings and column widths - bigger columns
        column_widths = {"ID": 80, "Name": 180, "Contact Person": 150, "Email": 180,
                        "Phone": 140, "Address": 220, "Credit Balance": 140, "Status": 100}
        
        for col in columns:
            self.data_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col in ["ID", "Credit Balance", "Status"] else "w", minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars with padding
        self.data_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        v_scrollbar.pack(side="right", fill="y", pady=5)
        h_scrollbar.pack(side="bottom", fill="x", padx=5)
        
        # Bind double-click to edit
        self.data_tree.bind("<Double-1>", lambda e: self.edit_supplier())
    
    def load_data(self):
        """Load suppliers data"""
        try:
            query = """
                SELECT supplier_id, name, contact_person, email, phone, address, 
                       credit_balance, is_active
                FROM suppliers
                ORDER BY name
            """
            suppliers = db.execute_query(query)
            
            # Clear existing items
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Add suppliers to tree
            for supplier in suppliers:
                status = "Active" if supplier['is_active'] else "Inactive"
                credit_balance = f"${supplier['credit_balance']:.2f}" if supplier['credit_balance'] else "$0.00"
                
                self.data_tree.insert("", "end", values=(
                    supplier['supplier_id'],
                    supplier['name'],
                    supplier['contact_person'] or "N/A",
                    supplier['email'] or "N/A",
                    supplier['phone'] or "N/A",
                    supplier['address'] or "N/A",
                    credit_balance,
                    status
                ))
            
            self.all_data = suppliers  # Store for filtering
            
        except Exception as e:
            print(f"Error loading suppliers: {e}")
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")
    
    def filter_data(self, *args):
        """Filter suppliers based on search and filters"""
        search_term = self.search_var.get().lower()
        status_filter = self.status_filter_var.get()
        credit_filter = self.credit_filter_var.get()
        
        # Clear tree
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not hasattr(self, 'all_data'):
            return
        
        # Filter and display matching suppliers
        for supplier in self.all_data:
            # Check search term
            matches_search = (
                search_term in supplier['name'].lower() or
                (supplier['contact_person'] and search_term in supplier['contact_person'].lower()) or
                (supplier['email'] and search_term in supplier['email'].lower()) or
                (supplier['phone'] and search_term in supplier['phone'].lower()) or
                (supplier['address'] and search_term in supplier['address'].lower())
            )
            
            # Check status filter
            supplier_status = "Active" if supplier['is_active'] else "Inactive"
            matches_status = status_filter == "All" or supplier_status == status_filter
            
            # Check credit filter
            has_credit = supplier['credit_balance'] > 0
            if credit_filter == "All":
                matches_credit = True
            elif credit_filter == "Has Credit":
                matches_credit = has_credit
            else:  # No Credit
                matches_credit = not has_credit
            
            if matches_search and matches_status and matches_credit:
                credit_balance = f"${supplier['credit_balance']:.2f}" if supplier['credit_balance'] else "$0.00"
                
                self.data_tree.insert("", "end", values=(
                    supplier['supplier_id'],
                    supplier['name'],
                    supplier['contact_person'] or "N/A",
                    supplier['email'] or "N/A",
                    supplier['phone'] or "N/A",
                    supplier['address'] or "N/A",
                    credit_balance,
                    supplier_status
                ))
    
    def clear_filters(self):
        """Clear all filters and reload data"""
        self.search_var.set("")
        self.status_filter_var.set("All")
        self.credit_filter_var.set("All")
        self.filter_data()
    
    def export_to_excel(self):
        """Export suppliers to Excel"""
        ExportManager.export_suppliers_to_excel()
    
    def export_to_pdf(self):
        """Export suppliers to PDF"""
        ExportManager.export_suppliers_to_pdf()
    
    def add_supplier(self):
        """Add new supplier"""
        dialog = SupplierDialog(self.parent, "Add Supplier")
        if dialog.result:
            try:
                db.execute_insert(
                    """INSERT INTO suppliers (name, contact_person, email, phone, address)
                       VALUES (?, ?, ?, ?, ?)""",
                    (dialog.result['name'], dialog.result['contact_person'],
                     dialog.result['email'], dialog.result['phone'], dialog.result['address'])
                )
                
                messagebox.showinfo("Success", "Supplier added successfully!")
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {e}")
    
    def edit_supplier(self):
        """Edit selected supplier"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to edit.")
            return
        
        # Get selected supplier data
        item_values = self.data_tree.item(selection[0], 'values')
        supplier_id = item_values[0]
        
        # Get full supplier data
        supplier_query = "SELECT * FROM suppliers WHERE supplier_id = ?"
        supplier_result = db.execute_query(supplier_query, (supplier_id,))
        
        if supplier_result:
            supplier = supplier_result[0]
            dialog = SupplierDialog(self.parent, "Edit Supplier", supplier)
            if dialog.result:
                try:
                    db.execute_update(
                        """UPDATE suppliers SET name=?, contact_person=?, email=?, phone=?, address=?
                           WHERE supplier_id=?""",
                        (dialog.result['name'], dialog.result['contact_person'],
                         dialog.result['email'], dialog.result['phone'], dialog.result['address'], supplier_id)
                    )
                    messagebox.showinfo("Success", "Supplier updated successfully!")
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update supplier: {e}")
    
    def delete_supplier(self):
        """Delete selected supplier"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to delete.")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this supplier?"):
            return
        
        item_values = self.data_tree.item(selection[0], 'values')
        supplier_id = item_values[0]
        
        try:
            # Set supplier as inactive instead of deleting
            db.execute_update("UPDATE suppliers SET is_active=0 WHERE supplier_id=?", (supplier_id,))
            messagebox.showinfo("Success", "Supplier deleted successfully!")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete supplier: {e}")


class SupplierDialog:
    def __init__(self, parent, title, supplier_data=None):
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        size_and_center_dialog(self.dialog, parent, 580, 700, min_w=480, min_h=550)
        
        # Create form
        self.create_form(supplier_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self, supplier_data):
        """Create supplier form with modern styling"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with icon
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#efebe9", "#5d4037"))
        header_frame.pack(fill="x", padx=15, pady=(15, 20))
        
        supplier_icon = ctk.CTkLabel(header_frame, text="🏦", font=ctk.CTkFont(size=28))
        supplier_icon.pack(pady=(15, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Supplier Information",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#3e2723", "white")
        )
        header_label.pack(pady=(0, 15))
        
        # Scrollable form fields container
        fields_container = ctk.CTkScrollableFrame(main_frame)
        fields_container.pack(fill="both", expand=True, padx=15)
        
        # Name field
        name_frame = ctk.CTkFrame(fields_container, corner_radius=10)
        name_frame.pack(fill="x", pady=(0, 12))
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="🏢 Supplier Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Enter supplier name...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Contact Person field
        contact_frame = ctk.CTkFrame(fields_container, corner_radius=10)
        contact_frame.pack(fill="x", pady=(0, 12))
        
        contact_label = ctk.CTkLabel(
            contact_frame,
            text="👤 Contact Person:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        contact_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.contact_entry = ctk.CTkEntry(
            contact_frame,
            placeholder_text="Enter contact person name...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.contact_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Email field
        email_frame = ctk.CTkFrame(fields_container, corner_radius=10)
        email_frame.pack(fill="x", pady=(0, 12))
        
        email_label = ctk.CTkLabel(
            email_frame,
            text="📧 Email Address:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        email_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.email_entry = ctk.CTkEntry(
            email_frame,
            placeholder_text="Enter email address...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.email_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Phone field
        phone_frame = ctk.CTkFrame(fields_container, corner_radius=10)
        phone_frame.pack(fill="x", pady=(0, 12))
        
        phone_label = ctk.CTkLabel(
            phone_frame,
            text="📱 Phone Number:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        phone_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.phone_entry = ctk.CTkEntry(
            phone_frame,
            placeholder_text="Enter phone number...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.phone_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Address field
        address_frame = ctk.CTkFrame(fields_container, corner_radius=10)
        address_frame.pack(fill="x", pady=(0, 12))
        
        address_label = ctk.CTkLabel(
            address_frame,
            text="🏠 Address:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        address_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.address_entry = ctk.CTkTextbox(
            address_frame,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.address_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Fill form if editing
        if supplier_data:
            self.name_entry.insert(0, supplier_data['name'] if supplier_data['name'] else '')
            self.contact_entry.insert(0, supplier_data['contact_person'] if supplier_data['contact_person'] else '')
            self.email_entry.insert(0, supplier_data['email'] if supplier_data['email'] else '')
            self.phone_entry.insert(0, supplier_data['phone'] if supplier_data['phone'] else '')
            if supplier_data['address']:
                self.address_entry.insert("0.0", supplier_data['address'])
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(15, 15))
        
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
            text="💾 Save Supplier",
            command=self.save_supplier,
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
    
    def save_supplier(self):
        """Save supplier data with validation"""
        try:
            # Validate required fields
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Supplier name is required.")
                return
            
            # Get form data
            contact_person = self.contact_entry.get().strip()
            email = self.email_entry.get().strip()
            phone = self.phone_entry.get().strip()
            address = self.address_entry.get("1.0", "end-1c").strip()
            
            # Basic email validation
            if email and "@" not in email:
                messagebox.showerror("Error", "Please enter a valid email address.")
                return
            
            self.result = {
                'name': name,
                'contact_person': contact_person or None,
                'email': email or None,
                'phone': phone or None,
                'address': address or None
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving supplier: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()
