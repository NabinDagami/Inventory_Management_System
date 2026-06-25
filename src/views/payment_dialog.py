import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from utils.format_utils import format_price_with_decimals, get_currency_symbol
from utils.dialog_utils import size_and_center_dialog


class PaymentDialog:
    def __init__(self, parent, payment_type="customer", customer_data=None, supplier_data=None):
        self.parent = parent
        self.payment_type = payment_type  # "customer" or "supplier"
        self.customer_data = customer_data
        self.supplier_data = supplier_data
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Record {payment_type.title()} Payment")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        self.create_form()
        size_and_center_dialog(self.dialog, parent, 500, 550, min_w=450, min_h=450)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_form(self):
        """Create payment form"""
        # Header (fixed)
        header_frame = ctk.CTkFrame(self.dialog, corner_radius=10, fg_color=("#e8f5e8", "#2d5a2d"))
        header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        # Payment icon
        payment_icon = ctk.CTkLabel(header_frame, text="💰", font=ctk.CTkFont(size=28))
        payment_icon.pack(pady=(10, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"Record {self.payment_type.title()} Payment",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1a5c1a", "white")
        )
        header_label.pack(pady=(0, 10))
        
        # Scrollable form fields
        fields_container = ctk.CTkScrollableFrame(self.dialog)
        fields_container.pack(fill="both", expand=True, padx=20, pady=(5, 0))
        
        # Form fields container
        fields_frame = ctk.CTkFrame(fields_container, fg_color="transparent")
        fields_frame.pack(fill="x", padx=0)
        
        # Customer/Supplier information display
        info_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        if self.payment_type == "customer" and self.customer_data:
            info_text = f"Customer: {self.customer_data['name']}\nType: {self.customer_data['type']}\nCurrent Credit Balance: {format_price_with_decimals(self.customer_data['credit_balance'])}"
        elif self.payment_type == "supplier" and self.supplier_data:
            info_text = f"Supplier: {self.supplier_data['name']}\nCurrent Credit Balance: {format_price_with_decimals(self.supplier_data['credit_balance'])}"
        else:
            info_text = "No customer/supplier selected"
            
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(padx=15, pady=15)
        
        # Payment Amount
        amount_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        amount_frame.pack(fill="x", pady=(0, 12))
        
        amount_label = ctk.CTkLabel(
            amount_frame,
            text=f"💵 Payment Amount ({get_currency_symbol()}) *:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        amount_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.amount_entry = ctk.CTkEntry(
            amount_frame,
            placeholder_text="Enter payment amount...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.amount_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Payment Method
        method_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        method_frame.pack(fill="x", pady=(0, 12))
        
        method_label = ctk.CTkLabel(
            method_frame,
            text="💳 Payment Method:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        method_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.payment_method_var = tk.StringVar(value="Cash")
        payment_method_dropdown = ctk.CTkOptionMenu(
            method_frame,
            variable=self.payment_method_var,
            values=["Cash", "Bank Transfer", "Check", "Credit Card"],
            width=200
        )
        payment_method_dropdown.pack(anchor="w", padx=15, pady=(0, 12))
        
        # Reference Number
        ref_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        ref_frame.pack(fill="x", pady=(0, 12))
        
        ref_label = ctk.CTkLabel(
            ref_frame,
            text="📄 Reference Number:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ref_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.reference_entry = ctk.CTkEntry(
            ref_frame,
            placeholder_text="Check number, transaction ID, etc.",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.reference_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Payment Date
        date_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        date_frame.pack(fill="x", pady=(0, 12))
        
        date_label = ctk.CTkLabel(
            date_frame,
            text="📅 Payment Date:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        date_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.date_entry.pack(fill="x", padx=15, pady=(0, 12))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Notes
        notes_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        notes_frame.pack(fill="x", pady=(0, 15))
        
        notes_label = ctk.CTkLabel(
            notes_frame,
            text="📝 Notes:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        notes_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.notes_text = ctk.CTkTextbox(
            notes_frame,
            height=60,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.notes_text.pack(fill="x", padx=15, pady=(0, 12))
        
        # Fixed footer with buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15))
        
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
            text="💾 Record Payment",
            command=self.record_payment,
            width=150,
            height=45,
            corner_radius=10,
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="right")
        
        # Focus on amount entry
        self.amount_entry.focus()
    
    def record_payment(self):
        """Record the payment transaction"""
        # Validate required fields
        if not self.amount_entry.get().strip():
            messagebox.showerror("Error", "Payment amount is required!")
            return
        
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showerror("Error", "Payment amount must be greater than 0!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid payment amount!")
            return
        
        # Validate payment date
        try:
            payment_date = datetime.strptime(self.date_entry.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format!")
            return
        
        # Check if payment amount exceeds credit balance
        if self.payment_type == "customer" and self.customer_data:
            if amount > self.customer_data['credit_balance']:
                if not messagebox.askyesno("Confirm", 
                        f"Payment amount ({format_price_with_decimals(amount)}) exceeds credit balance ({format_price_with_decimals(self.customer_data['credit_balance'])}).\n"
                        "This will result in a credit balance for the customer. Continue?"):
                    return
        elif self.payment_type == "supplier" and self.supplier_data:
            if amount > self.supplier_data['credit_balance']:
                if not messagebox.askyesno("Confirm", 
                        f"Payment amount ({format_price_with_decimals(amount)}) exceeds credit balance ({format_price_with_decimals(self.supplier_data['credit_balance'])}).\n"
                        "This will result in a credit balance for the supplier. Continue?"):
                    return
        
        try:
            # Record payment in payments table
            customer_id = self.customer_data['customer_id'] if self.payment_type == "customer" else None
            supplier_id = self.supplier_data['supplier_id'] if self.payment_type == "supplier" else None
            
            db.execute_insert("""
                INSERT INTO payments (payment_type, customer_id, supplier_id, amount, 
                                    payment_method, reference_number, notes, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.payment_type,
                customer_id,
                supplier_id,
                amount,
                self.payment_method_var.get(),
                self.reference_entry.get().strip() or None,
                self.notes_text.get("1.0", "end-1c").strip() or None,
                payment_date
            ))
            
            # Update customer/supplier credit balance
            if self.payment_type == "customer":
                db.execute_update("""
                    UPDATE customers 
                    SET credit_balance = credit_balance - ?
                    WHERE customer_id = ?
                """, (amount, customer_id))
                
                # Update any outstanding sales for this customer
                self.update_sales_payments(customer_id, amount)
                
            elif self.payment_type == "supplier":
                db.execute_update("""
                    UPDATE suppliers 
                    SET credit_balance = credit_balance - ?
                    WHERE supplier_id = ?
                """, (amount, supplier_id))
                
                # Update any outstanding purchases for this supplier
                self.update_purchase_payments(supplier_id, amount)
            
            messagebox.showinfo("Success", 
                f"Payment of {format_price_with_decimals(amount)} recorded successfully for {self.payment_type}!")
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            print(f"Error recording payment: {e}")
            messagebox.showerror("Error", f"Failed to record payment: {e}")
    
    def update_sales_payments(self, customer_id, payment_amount):
        """Update sales records when customer makes a payment"""
        try:
            # Get unpaid sales for this customer, ordered by date (oldest first)
            unpaid_sales = db.execute_query("""
                SELECT id, invoice_number, total_amount, paid_amount, balance 
                FROM sales 
                WHERE customer_id = ? AND balance > 0 AND status = 'credit'
                ORDER BY sale_date ASC, id ASC
            """, (customer_id,))
            
            remaining_payment = payment_amount
            
            for sale in unpaid_sales:
                if remaining_payment <= 0:
                    break
                    
                outstanding_balance = sale['balance']
                payment_for_this_sale = min(remaining_payment, outstanding_balance)
                
                new_paid_amount = sale['paid_amount'] + payment_for_this_sale
                new_balance = sale['total_amount'] - new_paid_amount
                new_status = 'completed' if new_balance <= 0.01 else 'credit'  # Allow small rounding differences
                
                # Update the sale record
                db.execute_update("""
                    UPDATE sales 
                    SET paid_amount = ?, balance = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_paid_amount, new_balance, new_status, sale['id']))
                
                remaining_payment -= payment_for_this_sale
                
        except Exception as e:
            print(f"Error updating sales payments: {e}")
    
    def update_purchase_payments(self, supplier_id, payment_amount):
        """Update purchase records when supplier receives a payment"""
        try:
            # Get unpaid purchases for this supplier, ordered by date (oldest first)
            unpaid_purchases = db.execute_query("""
                SELECT id, invoice_number, total_amount, paid_amount, balance 
                FROM purchases 
                WHERE supplier_id = ? AND balance > 0 AND status = 'credit'
                ORDER BY purchase_date ASC, id ASC
            """, (supplier_id,))
            
            remaining_payment = payment_amount
            
            for purchase in unpaid_purchases:
                if remaining_payment <= 0:
                    break
                    
                outstanding_balance = purchase['balance']
                payment_for_this_purchase = min(remaining_payment, outstanding_balance)
                
                new_paid_amount = purchase['paid_amount'] + payment_for_this_purchase
                new_balance = purchase['total_amount'] - new_paid_amount
                new_status = 'completed' if new_balance <= 0.01 else 'credit'
                
                # Update the purchase record
                db.execute_update("""
                    UPDATE purchases 
                    SET paid_amount = ?, balance = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_paid_amount, new_balance, new_status, purchase['id']))
                
                remaining_payment -= payment_for_this_purchase
                
        except Exception as e:
            print(f"Error updating purchase payments: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = False
        self.dialog.destroy()
