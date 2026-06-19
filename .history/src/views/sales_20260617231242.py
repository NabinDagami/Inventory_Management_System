import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from views.settings import SettingsView
import utils.simple_table_styles as table_styles
from utils.barcode_server import BarcodeServer
from utils.format_utils import format_price_with_decimals as _fmt, format_price as _fmt_int


def center_window_on_screen(window, width, height):
    """Center a window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


class SearchableDropdown(ctk.CTkFrame):
    """A custom searchable dropdown component for customer selection"""
    def __init__(self, parent, placeholder_text="Search...", width=250, command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.parent_widget = parent  # Renamed to avoid conflict
        self.command = command
        self.all_values = []
        self.filtered_values = []
        self.selected_value = None
        self.dropdown_window = None
        self.listbox = None
        
        # Container frame for horizontal layout
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(fill="x", expand=True)
        
        # Main entry field
        self.entry = ctk.CTkEntry(
            self.inner_frame,
            placeholder_text=placeholder_text,
            width=width - 40,
            height=32
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Dropdown button
        self.dropdown_btn = ctk.CTkButton(
            self.inner_frame,
            text="▼",
            width=30,
            height=32,
            command=self.toggle_dropdown
        )
        self.dropdown_btn.pack(side="left", padx=(5, 0))
        
        # Bind events
        self.entry.bind('<KeyRelease>', self.on_key_release)
        self.entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.entry.bind('<Down>', self.on_arrow_down)
        
        # Click outside to close dropdown - bind to toplevel window
        self._setup_click_binding()
    
    def _setup_click_binding(self):
        """Setup the click-outside binding after widget is fully created"""
        try:
            toplevel = self.winfo_toplevel()
            self._toplevel = toplevel
            func_id = toplevel.bind('<Button-1>', self.on_click_outside, add='+')
            self._click_binding_func_id = func_id
            self.bind('<Destroy>', self._cleanup_binding)
        except:
            pass
    
    def _cleanup_binding(self, event=None):
        """Remove the global click binding to prevent memory leaks"""
        try:
            if hasattr(self, '_toplevel') and self._toplevel and self._toplevel.winfo_exists():
                func_id = getattr(self, '_click_binding_func_id', None)
                if func_id:
                    self._toplevel.unbind('<Button-1>', funcid=func_id)
        except:
            pass
    
    def create_dropdown_window(self):
        """Create the dropdown Toplevel window"""
        if self.dropdown_window is not None:
            return
            
        # Create Toplevel window for dropdown
        self.dropdown_window = tk.Toplevel(self.winfo_toplevel())
        self.dropdown_window.overrideredirect(True)  # Remove window decorations
        self.dropdown_window.transient(self.winfo_toplevel())
        
        # Frame for content
        is_light = ctk.get_appearance_mode() == "Light"
        bg_color = "white" if is_light else "#1e1e1e"
        border_color = "#0078d4" if is_light else "#0078d4"  # Blue border for visibility
        
        outer_frame = tk.Frame(self.dropdown_window, bg=border_color, bd=2)
        outer_frame.pack(fill="both", expand=True)
        
        inner_frame = tk.Frame(outer_frame, bg=bg_color)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Listbox for dropdown items - improved visibility
        self.listbox = tk.Listbox(
            inner_frame,
            font=("Segoe UI", 13, "bold"),  # Larger, bolder font
            bg=bg_color,
            fg="black" if is_light else "white",
            selectbackground="#0078d4",  # Microsoft blue selection
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            activestyle="none",
            height=10,  # More visible items
            selectmode="single"
        )
        self.listbox.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Configure listbox item height for better visibility
        self.listbox.configure(height=8)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bind events for listbox
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        self.listbox.bind('<Return>', self.on_listbox_select)
        self.listbox.bind('<Escape>', self.hide_dropdown)
    
    def set_values(self, values):
        """Set the list of values for the dropdown"""
        self.all_values = values
        self.filtered_values = values.copy()
        if self.listbox:
            self.update_listbox()
    
    def get(self):
        """Get the current entry text"""
        return self.entry.get()
    
    def set(self, value):
        """Set the entry text"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.selected_value = value
    
    def on_key_release(self, event):
        """Handle typing in the entry field"""
        if event.keysym in ('Down', 'Up', 'Return', 'Escape'):
            return
        
        search_term = self.entry.get().lower()
        self.filtered_values = [v for v in self.all_values if search_term in v.lower()]
        
        if self.filtered_values:
            self.show_dropdown()
        else:
            self.hide_dropdown()
    
    def update_listbox(self):
        """Update the listbox with filtered values"""
        if self.listbox is None:
            return
        self.listbox.delete(0, tk.END)
        for value in self.filtered_values:
            self.listbox.insert(tk.END, value)
    
    def show_dropdown(self):
        """Show the dropdown below the entry"""
        if not self.filtered_values:
            return
        
        # Create dropdown window if not exists
        if self.dropdown_window is None:
            self.create_dropdown_window()
        
        # Update listbox content
        self.update_listbox()
        
        # Position dropdown below the entry - make it wider and taller
        x = self.inner_frame.winfo_rootx()
        y = self.inner_frame.winfo_rooty() + self.inner_frame.winfo_height()
        
        # Make dropdown wider than the entry field for better visibility
        entry_width = self.inner_frame.winfo_width()
        width = max(entry_width, 350)  # Minimum 350px width
        
        # Calculate height based on number of items, with min and max limits
        item_height = 28  # Height per item in pixels
        height = min(280, max(120, len(self.filtered_values) * item_height + 20))  # Min 120px, max 280px
        
        # Position and size the window
        self.dropdown_window.geometry(f"{width}x{height}+{x}+{y}")
        self.dropdown_window.deiconify()
        self.dropdown_window.lift()
        self.dropdown_window.focus_force()
    
    def hide_dropdown(self, event=None):
        """Hide the dropdown"""
        if self.dropdown_window:
            self.dropdown_window.withdraw()
    
    def toggle_dropdown(self):
        """Toggle dropdown visibility"""
        if self.dropdown_window and self.dropdown_window.winfo_viewable():
            self.hide_dropdown()
        else:
            self.filtered_values = self.all_values.copy()
            self.show_dropdown()
            self.entry.focus()
    
    def on_entry_focus_in(self, event):
        """Show dropdown when entry is focused"""
        if self.filtered_values:
            self.show_dropdown()
    
    def on_arrow_down(self, event):
        """Handle down arrow key"""
        if self.dropdown_window is None or not self.dropdown_window.winfo_viewable():
            self.filtered_values = self.all_values.copy()
            self.show_dropdown()
        if self.listbox and self.listbox.size() > 0:
            self.listbox.focus()
            self.listbox.selection_set(0)
    
    def on_listbox_select(self, event=None):
        """Handle selection from listbox"""
        if self.listbox is None:
            return
        selection = self.listbox.curselection()
        if selection:
            value = self.listbox.get(selection[0])
            self.set(value)
            self.hide_dropdown()
            self.entry.focus()
            if self.command:
                self.command(value)
    
    def on_click_outside(self, event):
        """Hide dropdown when clicking outside"""
        if self.dropdown_window and self.dropdown_window.winfo_viewable():
            # Check if click is inside the dropdown or the widget
            widget = event.widget
            try:
                # Get widget under mouse
                x, y = event.x_root, event.y_root
                
                # Check if click is in dropdown window
                dropdown_x = self.dropdown_window.winfo_rootx()
                dropdown_y = self.dropdown_window.winfo_rooty()
                dropdown_w = self.dropdown_window.winfo_width()
                dropdown_h = self.dropdown_window.winfo_height()
                
                in_dropdown = (dropdown_x <= x <= dropdown_x + dropdown_w and 
                              dropdown_y <= y <= dropdown_y + dropdown_h)
                
                # Check if click is in the entry/button
                entry_x = self.winfo_rootx()
                entry_y = self.winfo_rooty()
                entry_w = self.winfo_width()
                entry_h = self.winfo_height()
                
                in_entry = (entry_x <= x <= entry_x + entry_w and 
                           entry_y <= y <= entry_y + entry_h)
                
                if not in_dropdown and not in_entry:
                    self.hide_dropdown()
            except:
                pass


class SalesView:
    def __init__(self, parent):
        self.parent = parent
        self.cart_items = []
        self.current_customer = None
        self.discount_amount = 0
        self.discount_type = "amount"  # "amount" or "percentage"
        self.discount_percentage = 0
        self._barcode_server = None
        self._server_url = None

        # Prevent multiple increments from repeated scans of the same barcode
        # (common when a scanner/phone sends the same code several times in a burst)
        self._last_scanned_code = None
        self._last_scanned_ts_ms = 0
        self._scan_debounce_ms = 1200

        self.create_sales_interface()
        self.load_customers()
        self.load_products()
        self._start_barcode_server()
    
    def _start_barcode_server(self):
        try:
            self._barcode_server = BarcodeServer()
            self._barcode_server.start(self._on_remote_scan)
            self._server_url = self._barcode_server.url
        except Exception as e:
            self._barcode_server = None
            self._server_url = None
            print(f"Barcode server: {e}")

    def _on_remote_scan(self, code):
        self.parent.after(0, lambda: self._process_remote_scan(code))

    def _process_remote_scan(self, code):
        code = (code or "").strip()
        if not code:
            return

        # Debounce repeated scans of the same barcode
        now_ms = int(ctk.ctk_time.time() * 1000) if hasattr(ctk, "ctk_time") else None
        # Fallback: use Tk's time if available
        try:
            now_ms = int(self.parent.winfo_toplevel().tk.call('clock','milliseconds'))
        except Exception:
            import time as _time
            now_ms = int(_time.time() * 1000)

        if self._last_scanned_code == code and (now_ms - self._last_scanned_ts_ms) < self._scan_debounce_ms:
            return

        self._last_scanned_code = code
        self._last_scanned_ts_ms = now_ms

        self.barcode_var.set(code)
        self._on_barcode_scanned()

    def _toggle_scan_info(self):
        if not self._barcode_server:
            messagebox.showinfo(
                "Phone Scan",
                "Could not start the scanner server. Check network/antivirus.")
            return
        if self.scan_info.winfo_ismapped():
            self.scan_info.grid_remove()
            self.scan_btn.configure(text="📱 Phone Scan")
        else:
            url = self._server_url or "unknown"
            self.scan_info.configure(
                text=f"🔗 Open {url} on your phone → scan barcodes")
            self.scan_info.grid()
            self.scan_btn.configure(text="📱 Hide")

    def create_sales_interface(self):
        """Create the sales management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame)
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.new_sale_btn = ctk.CTkButton(
            tab_frame,
            text="💰 New Sale",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("new_sale")
        )
        self.new_sale_btn.pack(side="left", padx=(0, 10))
        
        self.sales_history_btn = ctk.CTkButton(
            tab_frame,
            text="📋 Sales History",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("sales_history")
        )
        self.sales_history_btn.pack(side="left", padx=(0, 10))

        self.credit_payments_btn = ctk.CTkButton(
            tab_frame,
            text="💳 Credit Payments",
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("credit_payments")
        )
        self.credit_payments_btn.pack(side="left")

        # Current tab tracking
        self.current_tab = "new_sale"
        
        # Content container
        self.content_container = ctk.CTkFrame(main_frame)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=0)
        
        # Create all interfaces
        self.create_new_sale_interface()
        self.create_sales_history_interface()
        self.create_credit_payments_interface()

        # Show new sale interface by default
        self.switch_tab("new_sale")
    
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab = tab_name

        # Update button styles
        active_color = ("#1f538d", "#14375e")
        inactive_color = ("gray85", "gray25")
        inactive_text_color = ("gray10", "gray90")
        
        if tab_name == "new_sale":
            self.new_sale_btn.configure(fg_color=active_color, text_color="white")
            self.sales_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_payments_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        elif tab_name == "sales_history":
            self.new_sale_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.sales_history_btn.configure(fg_color=active_color, text_color="white")
            self.credit_payments_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        else:  # credit_payments
            self.new_sale_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.sales_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.credit_payments_btn.configure(fg_color=active_color, text_color="white")

        # Hide all frames first
        self.new_sale_frame.pack_forget()
        self.sales_history_frame.pack_forget()
        self.credit_payments_frame.pack_forget()

        # Show the selected tab
        if tab_name == "new_sale":
            self.new_sale_frame.pack(fill="both", expand=True)
        elif tab_name == "sales_history":
            self.sales_history_frame.pack(fill="both", expand=True)
            self.load_sales_history()
        elif tab_name == "credit_payments":
            self.credit_payments_frame.pack(fill="both", expand=True)
            self.load_credit_sales()
    
    def create_new_sale_interface(self):
        """Create the new sale interface"""
        self.new_sale_frame = ctk.CTkFrame(self.content_container)
        
        # Customer and payment selection header
        header_frame = ctk.CTkFrame(self.new_sale_frame)
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
        content_frame = ctk.CTkFrame(self.new_sale_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        content_frame.grid_columnconfigure(0, weight=45)
        content_frame.grid_columnconfigure(1, weight=55)
        content_frame.grid_rowconfigure(0, weight=1)     # Allow row to expand fully
        
        # Left side - Product selection
        self.create_product_selection(content_frame)
        
        # Right side - Cart and total
        self.create_cart_section(content_frame)
    
    def create_sales_history_interface(self):
        """Create the sales history interface"""
        self.sales_history_frame = ctk.CTkFrame(self.content_container)
        
        # Header with search and filters
        header_frame = ctk.CTkFrame(self.sales_history_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(header_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.sales_search_var = ctk.StringVar()
        self.sales_search_var.trace('w', self.filter_sales_history)
        search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.sales_search_var,
            placeholder_text="Search by invoice number or customer...",
            width=300
        )
        search_entry.pack(side="left", padx=5, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_sales_history,
            width=100,
            height=35
        )
        refresh_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Sales history table
        table_frame = ctk.CTkFrame(self.sales_history_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=0)
        
        # Create container for the table (plain CTkFrame, not CTkScrollableFrame)
        table_container = ctk.CTkFrame(table_frame)
        table_container.pack(fill="both", expand=True)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Create treeview for sales history with enhanced styling
        columns = ("Invoice", "Date", "Customer", "Payment", "Items", "Discount", "Paid", "Credit", "Total", "Status")
        self.sales_history_tree = ttk.Treeview(table_container, columns=columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_sales_history_style(self.sales_history_tree)
        
        # Define headings and column widths - bigger columns
        column_widths = {"Invoice": 140, "Date": 110, "Customer": 180, "Payment": 90, 
                        "Items": 70, "Discount": 90, "Paid": 100, "Credit": 100, "Total": 110, "Status": 90}
        
        for col in columns:
            self.sales_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.sales_history_tree.column(col, width=column_widths.get(col, 120), anchor="center", minwidth=80)
        
        # Add both vertical and horizontal scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.sales_history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.sales_history_tree.xview)
        self.sales_history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars properly
        self.sales_history_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self.sales_history_frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        view_details_btn = ctk.CTkButton(
            actions_frame,
            text="👁️ View Details",
            command=self.view_sale_details,
            width=120,
            height=35
        )
        view_details_btn.pack(side="left", padx=5)

        pay_credit_btn = ctk.CTkButton(
            actions_frame,
            text="💰 Pay Credit",
            command=self.pay_credit_for_sale,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        pay_credit_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            actions_frame,
            text="🖨️ Export Invoice",
            command=self.export_invoice,
            width=130,
            height=35,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        export_btn.pack(side="left", padx=5)

        print_btn = ctk.CTkButton(
            actions_frame,
            text="🖨️ Print Bill",
            command=self.print_invoice,
            width=120,
            height=35,
            fg_color="#F59E0B",
            hover_color="#D97706",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        print_btn.pack(side="left", padx=5)

        # Double-click to view details
        self.sales_history_tree.bind("<Double-1>", lambda e: self.view_sale_details())
    
    def load_sales_history(self):
        """Load sales history data"""
        try:
            query = """
                SELECT s.id as sale_id, s.invoice_number, s.sale_date, s.payment_method,
                       s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as credit,
                       s.discount, s.status, c.name as customer_name,
                       COUNT(si.id) as item_count
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                LEFT JOIN sale_items si ON s.id = si.sale_id
                GROUP BY s.id
                ORDER BY s.sale_date DESC, s.id DESC
            """
            sales = db.execute_query(query)
            
            # Clear existing items
            for item in self.sales_history_tree.get_children():
                self.sales_history_tree.delete(item)
            
            # Add sales to tree with zebra striping
            for idx, sale in enumerate(sales):
                customer_name = sale['customer_name'] or "Walk-in Customer"
                payment_method = sale['payment_method'].title()
                status = sale['status'].title()
                discount_amount = sale['discount'] or 0
                
                self.sales_history_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    payment_method,
                    sale['item_count'],
                    _fmt(discount_amount) if discount_amount > 0 else "-",
                    _fmt(sale['paid_amount']),
                    _fmt(sale['total_amount'] - sale['paid_amount']),
                    _fmt(sale['total_amount']),
                    status
                ))
            
            self.all_sales_data = sales
            
        except Exception as e:
            print(f"Error loading sales history: {e}")
            messagebox.showerror("Error", f"Failed to load sales history: {e}")
    
    def filter_sales_history(self, *args):
        """Filter sales history based on search"""
        search_term = self.sales_search_var.get().lower()
        
        # Clear tree
        for item in self.sales_history_tree.get_children():
            self.sales_history_tree.delete(item)
        
        if not hasattr(self, 'all_sales_data'):
            return
        
        # Filter and display matching sales
        for idx, sale in enumerate(self.all_sales_data):
            customer_name = sale['customer_name'] or "Walk-in Customer"
            
            if (search_term in sale['invoice_number'].lower() or
                search_term in customer_name.lower()):
                
                payment_method = sale['payment_method'].title()
                status = sale['status'].title()
                discount_amount = sale['discount'] or 0
                
                self.sales_history_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    payment_method,
                    sale['item_count'],
                    _fmt(discount_amount) if discount_amount > 0 else "-",
                    _fmt(sale['paid_amount']),
                    _fmt(sale['total_amount'] - sale['paid_amount']),
                    _fmt(sale['total_amount']),
                    status
                ))
    
    def view_sale_details(self):
        """View detailed information about a selected sale"""
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to view details.")
            return
        
        # Get selected sale data
        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]
        
        # Find sale in data
        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break
        
        if not selected_sale:
            messagebox.showerror("Error", "Sale details not found.")
            return
        
        # Create details dialog
        SaleDetailsDialog(self.parent, selected_sale)
    
    def create_product_selection(self, parent):
        """Create product selection area"""
        # Use regular frame instead of scrollable frame
        product_frame = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"), corner_radius=6)
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
        
        # Search box + Barcode scanner row
        search_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 5))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(8, 5), pady=6)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.filter_products)
        search_entry = ctk.CTkEntry(
            search_frame, 
            textvariable=self.search_var,
            placeholder_text="Product name or SKU..."
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(5, 8), pady=6)
        
        # Barcode scanner entry
        barcode_label = ctk.CTkLabel(
            search_frame, text="📷 Barcode:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        barcode_label.grid(row=0, column=2, padx=(8, 5), pady=6)
        
        self.barcode_var = ctk.StringVar()
        self.barcode_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.barcode_var,
            placeholder_text="Scan barcode...",
            width=160
        )
        self.barcode_entry.grid(row=0, column=3, padx=(5, 8), pady=6)
        self.barcode_entry.bind("<Return>", self._on_barcode_scanned)

        # Mobile scanner link
        self.scan_btn = ctk.CTkButton(
            search_frame, text="📱 Phone Scan",
            width=28, height=28, corner_radius=6,
            fg_color="transparent",
            text_color=("blue", "#60A5FA"),
            hover_color=("gray85", "gray35"),
            font=ctk.CTkFont(size=12),
            command=self._toggle_scan_info
        )
        self.scan_btn.grid(row=0, column=4, padx=(0, 8), pady=6)

        self.scan_info = ctk.CTkLabel(
            search_frame, text="",
            font=ctk.CTkFont(size=11),
            text_color=("#2563EB", "#60A5FA"),
            anchor="w"
        )
        self.scan_info.grid(row=0, column=5, padx=(0, 8), pady=6)
        self.scan_info.grid_remove()
        
        # Products table container - this should expand to fill remaining space
        products_table_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        products_table_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 5))
        products_table_frame.grid_rowconfigure(0, weight=1)
        products_table_frame.grid_columnconfigure(0, weight=1)
        
        # Create container for products table
        products_container = ctk.CTkFrame(products_table_frame, fg_color="transparent", border_width=1, border_color=("gray80", "gray40"))
        products_container.grid(row=0, column=0, sticky="nsew")
        products_container.grid_rowconfigure(0, weight=1)
        products_container.grid_columnconfigure(0, weight=1)
        
        # Create treeview for products with enhanced styling
        columns = ("SKU", "Name", "Stock", "Normal Price", "Workshop Price")
        self.products_tree = ttk.Treeview(products_container, columns=columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_sales_products_style(self.products_tree)
        
        # Stock status tag styles (foreground only so selection color isn't overridden)
        is_dark = ctk.get_appearance_mode() == "Dark"
        self.products_tree.tag_configure("stock_zero", foreground=("#DC2626" if not is_dark else "#F87171"), font=("Segoe UI", 11, "bold"))
        self.products_tree.tag_configure("stock_low",  foreground=("#D97706" if not is_dark else "#FBBF24"), font=("Segoe UI", 11, "bold"))
        self.products_tree.tag_configure("stock_ok",   foreground=("#059669" if not is_dark else "#34D399"), font=("Segoe UI", 11))
        
        # Selection highlight via tags (reliable across ttk themes)
        self.products_tree.tag_configure("selected", background="#1565C0", foreground="#FFFFFF")
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Column widths and alignment
        column_widths = {"SKU": 90, "Name": 260, "Stock": 100, "Normal Price": 110, "Workshop Price": 110}
        column_anchors = {"SKU": "center", "Name": "w", "Stock": "center", "Normal Price": "e", "Workshop Price": "e"}
        column_minwidths = {"SKU": 60, "Name": 150, "Stock": 60, "Normal Price": 60, "Workshop Price": 60}
        for col in columns:
            self.products_tree.heading(col, text=col, anchor=column_anchors[col])
            self.products_tree.column(col, width=column_widths[col], anchor=column_anchors[col], minwidth=column_minwidths[col], stretch=(col == "Name"))
        
        # Add both scrollbars
        v_scrollbar = ttk.Scrollbar(products_container, orient="vertical", command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(products_container, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.products_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bottom controls: row count + add to cart
        controls_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        controls_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(5, 8))
        
        self.product_count_label = ctk.CTkLabel(controls_frame, text="Showing 0 products", font=ctk.CTkFont(size=11), text_color=("gray50", "gray60"))
        self.product_count_label.pack(side="left", padx=4, pady=3)
        
        add_cart_button = ctk.CTkButton(
            controls_frame,
            text="🛒 Add to Cart",
            command=lambda: self.add_to_cart(1),
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            width=180,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        add_cart_button.pack(side="right", padx=4, pady=3)
        
        # Bind double-click to add to cart
        self.products_tree.bind("<Double-1>", lambda e: self.add_to_cart())
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        cart_frame = ctk.CTkScrollableFrame(parent, label_text="🛒 Shopping Cart", fg_color=("#F5F5F5", "#252535"))
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        
        
        # Cart items table - make responsive with minimum height
        cart_table_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
        cart_table_frame.pack(fill="both", expand=True, padx=12, pady=(8, 10))
        
        # Create container for cart table
        cart_container = ctk.CTkFrame(cart_table_frame, fg_color="transparent")
        cart_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for cart with enhanced styling
        cart_columns = ("Product", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_container, columns=cart_columns, show="headings")
        
        # Apply centralized styling
        table_styles.apply_cart_style(self.cart_tree)
        
        # Cart row styles (foreground only so selection color isn't overridden)
        is_dark = ctk.get_appearance_mode() == "Dark"
        self.cart_tree.tag_configure("cart_total", font=("Segoe UI", 11, "bold"), foreground=("#1565C0" if not is_dark else "#60A5FA"))
        
        # Selection highlight via tags
        self.cart_tree.tag_configure("selected", background="#1565C0", foreground="#FFFFFF")
        self.cart_tree.bind("<<TreeviewSelect>>", self.on_cart_select)
        
        # Define headings with optimized spacing
        column_widths = {"Product": 160, "Qty": 60, "Price": 90, "Total": 90}
        for col in cart_columns:
            self.cart_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.cart_tree.column(col, width=column_widths.get(col, 100), anchor="center" if col != "Product" else "w", minwidth=60)
        
        # Add both scrollbars
        v_scrollbar = ttk.Scrollbar(cart_container, orient="vertical", command=self.cart_tree.yview)
        h_scrollbar = ttk.Scrollbar(cart_container, orient="horizontal", command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        cart_container.grid_rowconfigure(0, weight=1)
        cart_container.grid_columnconfigure(0, weight=1)
        
        # Cart actions
        actions_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=12, pady=(8, 10))
        
        remove_button = ctk.CTkButton(
            actions_frame,
            text="❌ Remove Item",
            command=self.remove_from_cart,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        remove_button.pack(side="left", padx=(8, 5))
        
        dec_button = ctk.CTkButton(
            actions_frame,
            text="− Qty",
            command=self.decrease_cart_quantity,
            width=60,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FF6B35",
            hover_color="#e05a2b"
        )
        dec_button.pack(side="left", padx=2)
        
        inc_button = ctk.CTkButton(
            actions_frame,
            text="+ Qty",
            command=self.increase_cart_quantity,
            width=60,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        inc_button.pack(side="left", padx=2)
        
        clear_button = ctk.CTkButton(
            actions_frame,
            text="🗑 Clear Cart",
            command=self.clear_cart,
            width=100,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        clear_button.pack(side="left", padx=(5, 8))
        
        # No discount button here - moved to totals section
        
        # Discount section
        discount_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
        discount_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        discount_header = ctk.CTkLabel(
            discount_frame,
            text="💸 Discount",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        discount_header.pack(pady=(8, 5))
        
        # Discount type selection
        discount_type_frame = ctk.CTkFrame(discount_frame, fg_color="transparent")
        discount_type_frame.pack(fill="x", padx=8, pady=(0, 5))
        
        self.discount_type_var = tk.StringVar(value="amount")
        
        amount_radio = ctk.CTkRadioButton(
            discount_type_frame,
            text="Amount (Rs)",
            variable=self.discount_type_var,
            value="amount",
            command=self.on_discount_type_change,
            font=ctk.CTkFont(size=11)
        )
        amount_radio.pack(side="left", padx=(8, 15))
        
        percentage_radio = ctk.CTkRadioButton(
            discount_type_frame,
            text="Percentage (%)",
            variable=self.discount_type_var,
            value="percentage",
            command=self.on_discount_type_change,
            font=ctk.CTkFont(size=11)
        )
        percentage_radio.pack(side="left", padx=(0, 8))
        
        # Discount input section
        discount_input_frame = ctk.CTkFrame(discount_frame, fg_color="transparent")
        discount_input_frame.pack(fill="x", padx=8, pady=(0, 5))
        
        self.discount_entry = ctk.CTkEntry(
            discount_input_frame,
            placeholder_text="Enter discount amount...",
            width=120,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.discount_entry.pack(side="left", padx=(8, 5), pady=5)
        
        # Bind entry changes to update totals
        self.discount_entry.bind('<KeyRelease>', self.on_discount_change)
        
        apply_discount_btn = ctk.CTkButton(
            discount_input_frame,
            text="Apply",
            command=self.apply_inline_discount,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        apply_discount_btn.pack(side="left", padx=(0, 5), pady=5)
        
        clear_discount_btn = ctk.CTkButton(
            discount_input_frame,
            text="Clear",
            command=self.clear_inline_discount,
            width=50,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        clear_discount_btn.pack(side="left", padx=(0, 8), pady=5)
        
        # Totals section
        totals_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
        totals_frame.pack(fill="x", padx=10, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(
            totals_frame, 
            text=_fmt(0),  # placeholder
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.subtotal_label.pack(pady=(8, 2))
        
        self.discount_label = ctk.CTkLabel(
            totals_frame, 
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.discount_label.pack(pady=2)
        
        self.total_label = ctk.CTkLabel(
            totals_frame, 
            text=f"Total: {_fmt(0)}",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.total_label.pack(pady=(2, 8))
        
        # Process sale button
        process_button = ctk.CTkButton(
            cart_frame,
            text="💰 Process Sale",
            command=self.process_sale,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="green",
            hover_color="darkgreen"
        )
        process_button.pack(fill="x", padx=10, pady=8)
    
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
            self.customer_dropdown.set("Walk-in Customer")
            
        except Exception as e:
            print(f"Error loading customers: {e}")
    
    def load_products(self):
        """Load products for selection"""
        try:
            query = """
                SELECT p.product_id, p.sku, p.name, p.stock, p.price_normal, 
                       p.price_workshop, p.reorder_level, p.barcode
                FROM products p
                WHERE p.is_active = 1 AND p.stock > 0
                ORDER BY p.name
            """
            products = db.execute_query(query)
            
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Add products to tree
            for idx, product in enumerate(products):
                available = self.get_available_stock(product)
                reorder = product['reorder_level']
                if available <= 0:
                    stock_tag = "stock_zero"
                    stock_display = f"{available}  Out"
                elif available <= reorder:
                    stock_tag = "stock_low"
                    stock_display = f"{available}  Low"
                else:
                    stock_tag = "stock_ok"
                    stock_display = f"{available}"
                
                row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
                
                self.products_tree.insert("", "end", values=(
                    product['sku'],
                    product['name'],
                    stock_display,
                    _fmt(product['price_normal']),
                    _fmt(product['price_workshop'])
                ), tags=(stock_tag,))
            
            if hasattr(self, 'product_count_label'):
                self.product_count_label.configure(text=f"Showing {len(products)} products")
            
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
        filtered = []
        for product in self.all_products:
            if (search_term in product['name'].lower() or 
                search_term in product['sku'].lower() or
                (product.get('barcode') and search_term in product['barcode'].lower())):
                filtered.append(product)
        
        for idx, product in enumerate(filtered):
            available = self.get_available_stock(product)
            reorder = product['reorder_level']
            if available <= 0:
                stock_tag = "stock_zero"
                stock_display = f"{available}  Out"
            elif available <= reorder:
                stock_tag = "stock_low"
                stock_display = f"{available}  Low"
            else:
                stock_tag = "stock_ok"
                stock_display = f"{available}"
            
            self.products_tree.insert("", "end", values=(
                product['sku'],
                product['name'],
                stock_display,
                _fmt(product['price_normal']),
                _fmt(product['price_workshop'])
            ), tags=(stock_tag,))
        
        if hasattr(self, 'product_count_label'):
            self.product_count_label.configure(text=f"Showing {len(filtered)} products")
    def refresh_table_tags(self):
        """Re-apply zebra striping and stock status tag colors for current theme."""
        is_dark = ctk.get_appearance_mode() == "Dark"
        # Products tree
        if hasattr(self, 'products_tree') and self.products_tree and self.products_tree.winfo_exists():
            self.products_tree.tag_configure("stock_zero", foreground=("#DC2626" if not is_dark else "#F87171"), font=("Segoe UI", 11, "bold"))
            self.products_tree.tag_configure("stock_low",  foreground=("#D97706" if not is_dark else "#FBBF24"), font=("Segoe UI", 11, "bold"))
            self.products_tree.tag_configure("stock_ok",   foreground=("#059669" if not is_dark else "#34D399"), font=("Segoe UI", 11))
        # Cart tree
        if hasattr(self, 'cart_tree') and self.cart_tree and self.cart_tree.winfo_exists():
            pass
        # Sales history tree
        if hasattr(self, 'sales_history_tree') and self.sales_history_tree and self.sales_history_tree.winfo_exists():
            pass

    def get_cart_quantity(self, product_id):
        """Get total quantity of a product currently in the cart."""
        total = 0
        for item in self.cart_items:
            if item['product_id'] == product_id:
                total += item['quantity']
        return total

    def get_available_stock(self, product):
        """Calculate available stock = actual stock - quantity in cart."""
        in_cart = self.get_cart_quantity(product['product_id'])
        return product['stock'] - in_cart

    def refresh_products_display(self):
        """Refresh the products tree to show available stock (accounting for cart)."""
        if not hasattr(self, 'products_tree') or not self.products_tree:
            return
        for item_id in self.products_tree.get_children():
            values = self.products_tree.item(item_id, 'values')
            sku = values[0]
            product = None
            for p in self.all_products:
                if p['sku'] == sku:
                    product = p
                    break
            if not product:
                continue
            available = self.get_available_stock(product)
            reorder = product['reorder_level']
            if available <= 0:
                stock_tag = "stock_zero"
                stock_display = f"{available}  Out"
            elif available <= reorder:
                stock_tag = "stock_low"
                stock_display = f"{available}  Low"
            else:
                stock_tag = "stock_ok"
                stock_display = f"{available}"
            current_tags = list(self.products_tree.item(item_id, 'tags'))
            new_tags = [stock_tag]
            if "selected" in current_tags:
                new_tags.append("selected")
            self.products_tree.item(item_id, values=(
                values[0], values[1], stock_display, values[3], values[4]
            ), tags=tuple(new_tags))


    def on_product_select(self, event=None):
        """Handle product selection — apply selected tag for reliable highlight."""
        tree = self.products_tree
        for item in tree.get_children():
            tags = list(tree.item(item, 'tags'))
            if "selected" in tags:
                tags.remove("selected")
                tree.item(item, tags=tuple(tags))
        sel = tree.selection()
        if sel:
            tags = list(tree.item(sel[0], 'tags'))
            if "selected" not in tags:
                tags.append("selected")
                tree.item(sel[0], tags=tuple(tags))

    
    def on_cart_select(self, event=None):
        """Handle cart item selection — apply selected tag for reliable highlight."""
        tree = self.cart_tree
        for item in tree.get_children():
            tags = list(tree.item(item, 'tags'))
            if "selected" in tags:
                tags.remove("selected")
                tree.item(item, tags=tuple(tags))
        sel = tree.selection()
        if sel:
            tags = list(tree.item(sel[0], 'tags'))
            if "selected" not in tags:
                tags.append("selected")
                tree.item(sel[0], tags=tuple(tags))


    def on_customer_selected(self, customer_name):
        """Handle customer selection"""
        self.current_customer = self.customers_data.get(customer_name)
        self.update_cart_display()
    
    def _on_barcode_scanned(self, event=None):
        """Handle barcode scanner input — find product and add to cart.
        Adds directly via product data so it works even when the tree
        is filtered and the scanned item isn't visible."""
        code = self.barcode_var.get().strip()
        if not code:
            return
        self.barcode_var.set("")
        product = None
        for p in self.all_products:
            if p.get('barcode') and p['barcode'] == code:
                product = p
                break
        if not product:
            messagebox.showwarning(
                "Not Found",
                f"No product found with barcode: {code}")
            self.barcode_entry.focus_set()
            return
        quantity = 1
        available = self.get_available_stock(product)
        if quantity > available:
            if available <= 0:
                messagebox.showwarning("Out of Stock", f"{product['name']} is out of stock or all in cart.")
                self.barcode_entry.focus_set()
                return
            quantity = available
        for item in self.cart_items:
            if item['product_id'] == product['product_id']:
                messagebox.showinfo("Already in Cart", f"{product['name']} is already in the cart.")
                self.barcode_entry.focus_set()
                return
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
        self.barcode_entry.focus_set()

    def add_to_cart(self, quantity=1):
        """Add selected product to cart with specified quantity"""
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
        
        # Validate quantity
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        available = self.get_available_stock(product)
        if quantity > available:
            if available <= 0:
                messagebox.showwarning("Warning", f"No more units available for {product['name']} (all in cart).")
                return
            messagebox.showwarning("Warning", f"Only {available} units available. Adding {available} to cart.")
            quantity = available
        
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
                available = product['stock'] - existing_item['quantity']
                if available > 0:
                    messagebox.showwarning("Warning", f"Only {available} more units can be added.")
                    existing_item['quantity'] = product['stock']
                else:
                    messagebox.showwarning("Warning", "Maximum quantity already in cart.")
                    return
            else:
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
    
    def add_custom_quantity(self):
        """Add product to cart with custom quantity"""
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
        available = self.get_available_stock(product)
        quantity_str = tk.simpledialog.askstring(
            "Quantity", 
            f"Enter quantity for {product['name']}\n(Available: {available})"
        )
        
        if quantity_str:
            try:
                quantity = int(quantity_str)
                self.add_to_cart(quantity)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
    
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

    def decrease_cart_quantity(self):
        """Decrease quantity of selected cart item by 1."""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to decrease quantity.")
            return
        item_index = self.cart_tree.index(selection[0])
        if 0 <= item_index < len(self.cart_items):
            if self.cart_items[item_index]['quantity'] > 1:
                self.cart_items[item_index]['quantity'] -= 1
            else:
                self.cart_items.pop(item_index)
            self.update_cart_display()

    def increase_cart_quantity(self):
        """Increase quantity of selected cart item by 1, respecting available stock."""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to increase quantity.")
            return
        item_index = self.cart_tree.index(selection[0])
        if 0 <= item_index < len(self.cart_items):
            item = self.cart_items[item_index]
            product = None
            for p in self.all_products:
                if p['product_id'] == item['product_id']:
                    product = p
                    break
            if product:
                available = self.get_available_stock(product)
                if available <= 0:
                    messagebox.showwarning("Warning", "No more units available for this product.")
                    return
                self.cart_items[item_index]['quantity'] += 1
            self.update_cart_display()

    def update_cart_display(self):
        """Update cart display and totals"""
        # Save current selection before clearing
        selected_sku = None
        selected = self.cart_tree.selection()
        if selected:
            idx = self.cart_tree.index(selected[0])
            if 0 <= idx < len(self.cart_items):
                selected_sku = self.cart_items[idx]['sku']

        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        subtotal = 0
        customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
        
        # Add items to cart tree
        for idx, item in enumerate(self.cart_items):
            # Determine price based on customer type
            if customer_type == 'Workshop':
                unit_price = item['price_workshop']
            else:
                unit_price = item['price_normal']
            
            total_price = unit_price * item['quantity']
            subtotal += total_price
            
            item_id = self.cart_tree.insert("", "end", values=(
                item['name'][:20] + "..." if len(item['name']) > 20 else item['name'],
                item['quantity'],
                _fmt(unit_price),
                _fmt(total_price)
            ), tags=())
            
            # Re-select the previously selected item
            if selected_sku and item['sku'] == selected_sku:
                self.cart_tree.selection_set(item_id)
                self.cart_tree.focus(item_id)
                # Apply selected tag directly (in case <<TreeviewSelect>> doesn't fire)
                self.cart_tree.item(item_id, tags=("selected",))
        
        # Calculate discount and final total
        discount_amount = 0
        if self.discount_amount > 0 or self.discount_percentage > 0:
            if self.discount_type == "amount":
                discount_amount = min(self.discount_amount, subtotal)
            else:  # percentage
                discount_amount = (subtotal * self.discount_percentage) / 100
        
        final_total = subtotal - discount_amount
        
        # Update totals
        self.subtotal_label.configure(text=f"Subtotal: {_fmt(subtotal)}")
        
        if discount_amount > 0:
            if self.discount_type == "amount":
                discount_text = f"Discount: -Rs{discount_amount:.2f}"
            else:
                discount_text = f"Discount ({self.discount_percentage:.1f}%): -Rs{discount_amount:.2f}"
            self.discount_label.configure(text=discount_text)
        else:
            self.discount_label.configure(text="")
        
        self.total_label.configure(text=f"Total: Rs{final_total:.2f}")

        self.refresh_products_display()
    
    def create_credit_payments_interface(self):
        """Create the Credit Payments tab — shows all outstanding credit sales."""
        self.credit_payments_frame = ctk.CTkFrame(self.content_container)

        # Outer scrollable container so everything is reachable
        scroll = ctk.CTkScrollableFrame(self.credit_payments_frame)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header_frame = ctk.CTkFrame(scroll)
        header_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="💳 Outstanding Credit Sales",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_credit_sales,
            width=100,
            height=35
        ).pack(side="right", padx=10, pady=10)

        # Summary bar
        self.credit_summary_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.credit_summary_label.pack(padx=10, pady=(0, 5))

        # Outstanding credit sales table (fixed height so it doesn't push history off screen)
        table_frame = ctk.CTkFrame(scroll)
        table_frame.pack(fill="x", padx=10, pady=0)

        table_container = ctk.CTkFrame(table_frame)
        table_container.pack(fill="x", padx=5, pady=5)
        table_container.grid_columnconfigure(0, weight=1)

        columns = ("Invoice", "Date", "Customer", "Total", "Paid", "Outstanding")
        self.credit_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=8)

        col_widths = {"Invoice": 160, "Date": 110, "Customer": 220,
                      "Total": 120, "Paid": 120, "Outstanding": 130}
        for col in columns:
            self.credit_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.credit_tree.column(col, width=col_widths.get(col, 120), anchor="center", minwidth=80)

        v_sb = ttk.Scrollbar(table_container, orient="vertical", command=self.credit_tree.yview)
        h_sb = ttk.Scrollbar(table_container, orient="horizontal", command=self.credit_tree.xview)
        self.credit_tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)

        self.credit_tree.grid(row=0, column=0, sticky="ew")
        v_sb.grid(row=0, column=1, sticky="ns")
        h_sb.grid(row=1, column=0, sticky="ew")

        # Action buttons
        actions_frame = ctk.CTkFrame(scroll)
        actions_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            actions_frame,
            text="💰 Record Payment",
            command=self.pay_credit_from_tab,
            width=150,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=5)

        # Double-click to pay
        self.credit_tree.bind("<Double-1>", lambda e: self.pay_credit_from_tab())

        # ── Payment History section ──────────────────────────────────────
        history_header = ctk.CTkFrame(scroll)
        history_header.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(
            history_header,
            text="📜 Credit Payment History",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=8)

        history_table_frame = ctk.CTkFrame(scroll)
        history_table_frame.pack(fill="x", padx=10, pady=(0, 10))

        history_container = ctk.CTkFrame(history_table_frame)
        history_container.pack(fill="x", padx=5, pady=5)
        history_container.grid_columnconfigure(0, weight=1)

        hist_cols = ("Date", "Invoice", "Customer", "Amount Paid", "Remaining After", "Recorded At")
        self.payment_history_tree = ttk.Treeview(history_container, columns=hist_cols, show="headings", height=8)

        hist_widths = {"Date": 100, "Invoice": 160, "Customer": 180,
                       "Amount Paid": 120, "Remaining After": 130, "Recorded At": 150}
        for col in hist_cols:
            self.payment_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.payment_history_tree.column(col, width=hist_widths.get(col, 120), anchor="center", minwidth=80)

        ph_vsb = ttk.Scrollbar(history_container, orient="vertical", command=self.payment_history_tree.yview)
        ph_hsb = ttk.Scrollbar(history_container, orient="horizontal", command=self.payment_history_tree.xview)
        self.payment_history_tree.configure(yscrollcommand=ph_vsb.set, xscrollcommand=ph_hsb.set)

        self.payment_history_tree.grid(row=0, column=0, sticky="ew")
        ph_vsb.grid(row=0, column=1, sticky="ns")
        ph_hsb.grid(row=1, column=0, sticky="ew")

    def load_credit_sales(self):
        """Load all outstanding credit sales into the Credit Payments tab."""
        try:
            query = """
                SELECT s.id as sale_id, s.invoice_number, s.sale_date,
                       s.total_amount, s.paid_amount,
                       (s.total_amount - s.paid_amount) as outstanding,
                       c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.status = 'credit' AND (s.total_amount - s.paid_amount) > 0
                ORDER BY s.sale_date ASC, s.id ASC
            """
            sales = db.execute_query(query)

            for item in self.credit_tree.get_children():
                self.credit_tree.delete(item)

            total_outstanding = 0
            for sale in sales:
                customer_name = sale['customer_name'] or "Walk-in Customer"
                outstanding = sale['outstanding']
                total_outstanding += outstanding
                self.credit_tree.insert("", "end", values=(
                    sale['invoice_number'],
                    sale['sale_date'],
                    customer_name,
                    _fmt(sale['total_amount']),
                    _fmt(sale['paid_amount']),
                    _fmt(outstanding)
                ))

            self.all_credit_sales = sales
            count = len(sales)
            self.credit_summary_label.configure(
                text=f"{count} outstanding credit sale(s)  |  Total due: Rs{total_outstanding:.2f}"
            )

        except Exception as e:
            print(f"Error loading credit sales: {e}")
            messagebox.showerror("Error", f"Failed to load credit sales: {e}")

        # Also refresh payment history
        self.load_payment_history()

    def load_payment_history(self):
        """Load credit payment history into the history table."""
        try:
            query = """
                SELECT
                    p.payment_date,
                    s.invoice_number,
                    c.name as customer_name,
                    p.amount,
                    p.notes,
                    p.created_at
                FROM payments p
                LEFT JOIN customers c ON p.customer_id = c.customer_id
                LEFT JOIN sales s ON p.reference_number = s.invoice_number
                WHERE p.payment_type = 'sale_credit_payment'
                ORDER BY p.created_at DESC
            """
            records = db.execute_query(query)

            for item in self.payment_history_tree.get_children():
                self.payment_history_tree.delete(item)

            for rec in records:
                customer_name = rec['customer_name'] or "Walk-in Customer"
                invoice = rec['invoice_number'] or "-"
                # notes stores "remaining:X" so we parse it
                remaining = "-"
                try:
                    if rec['notes'] and rec['notes'].startswith("remaining:"):
                        remaining = _fmt(float(rec['notes'].split(':')[1]))
                except Exception:
                    pass

                self.payment_history_tree.insert("", "end", values=(
                    rec['payment_date'],
                    invoice,
                    customer_name,
                    _fmt(rec['amount']),
                    remaining,
                    rec['created_at']
                ))

        except Exception as e:
            print(f"Error loading payment history: {e}")

    def pay_credit_from_tab(self):
        """Pay credit for a sale selected in the Credit Payments tab."""
        selection = self.credit_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credit sale to pay.")
            return

        item_values = self.credit_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        selected_sale = None
        for sale in self.all_credit_sales:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        dialog = PaySaleCreditDialog(self.parent, selected_sale)
        if dialog.result:
            self.load_credit_sales()  # Refresh the tab

    def pay_credit_for_sale(self):
        """Pay off credit for a selected credit sale from Sales History."""
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to pay credit for.")
            return

        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        # Find the sale in loaded data
        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        # Check it is actually a credit sale with outstanding balance
        balance = selected_sale['total_amount'] - selected_sale['paid_amount']
        if balance <= 0:
            messagebox.showinfo("No Balance", f"Invoice {invoice_number} is already fully paid.")
            return

        if selected_sale['status'] != 'credit':
            messagebox.showinfo("Not a Credit Sale", f"Invoice {invoice_number} is not a credit sale.")
            return

        # Open the pay-credit dialog
        dialog = PaySaleCreditDialog(self.parent, selected_sale)
        if dialog.result:
            self.load_sales_history()  # Refresh the table

    def export_invoice(self):
        """Export a text invoice for the selected sale."""
        from tkinter import filedialog
        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to export.")
            return

        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        # Load sale items
        try:
            items = db.execute_query("""
                SELECT si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """, (selected_sale['sale_id'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sale items: {e}")
            return

        # Build receipt text
        sep = "=" * 48
        thin = "-" * 48
        customer_name = selected_sale['customer_name'] or "Walk-in Customer"
        discount = selected_sale['discount'] or 0

        lines = [
            sep,
            "           INVENTORY PRO",
            "            Sales Invoice",
            sep,
            f"  Invoice : {selected_sale['invoice_number']}",
            f"  Date    : {selected_sale['sale_date']}",
            f"  Customer: {customer_name}",
            f"  Payment : {selected_sale['payment_method'].title()}",
            f"  Status  : {selected_sale['status'].title()}",
            thin,
            f"  {'Product':<22} {'Qty':>4} {'Price':>8} {'Total':>8}",
            thin,
        ]

        for item in items:
            name = item['name'][:22]
            lines.append(f"  {name:<22} {item['quantity']:>4} {item['unit_price']:>8.2f} {item['total']:>8.2f}")

        lines += [
            thin,
            f"  {'Subtotal':<30} Rs{selected_sale['total_amount'] + discount:>8.2f}",
        ]
        if discount > 0:
            lines.append(f"  {'Discount':<30} Rs{discount:>8.2f}")
        lines += [
            f"  {'TOTAL':<30} Rs{selected_sale['total_amount']:>8.2f}",
            f"  {'Paid':<30} Rs{selected_sale['paid_amount']:>8.2f}",
        ]
        balance = selected_sale['total_amount'] - selected_sale['paid_amount']
        if balance > 0:
            lines.append(f"  {'Balance Due':<30} Rs{balance:>8.2f}")
        lines += [
            sep,
            "        Thank you for your business!",
            sep,
            f"  Printed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        receipt_text = "\n".join(lines)

        # Ask where to save
        filename = filedialog.asksaveasfilename(
            title="Save Invoice",
            initialfile=f"{invoice_number}.txt",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(receipt_text)
            messagebox.showinfo("Invoice Exported", f"✅ Invoice saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def print_invoice(self):
        """Print a PDF invoice for the selected sale with company info from settings."""
        import threading as _threading

        selection = self.sales_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to print.")
            return

        item_values = self.sales_history_tree.item(selection[0], 'values')
        invoice_number = item_values[0]

        selected_sale = None
        for sale in self.all_sales_data:
            if sale['invoice_number'] == invoice_number:
                selected_sale = sale
                break

        if not selected_sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        try:
            items = db.execute_query("""
                SELECT si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """, (selected_sale['sale_id'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sale items: {e}")
            return

        settings = SettingsView.get_settings()
        company = settings.get('company', {})
        defaults = settings.get('defaults', {})
        currency = defaults.get('currency', 'Rs')
        company_name = company.get('name', 'Your Company')
        company_address = company.get('address', '')
        company_phone = company.get('phone', '')
        company_email = company.get('email', '')
        logo_path = company.get('logo_path', '')
        has_logo = bool(logo_path and os.path.exists(logo_path))

        customer_name = selected_sale['customer_name'] or "Walk-in Customer"
        discount = selected_sale['discount'] or 0

        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = os.path.join(reports_dir, f"invoice_{invoice_number}.pdf")

        # --- Loading overlay ---
        loading = ctk.CTkToplevel(self.parent)
        loading.title("")
        loading.geometry("260x100")
        loading.resizable(False, False)
        loading.transient(self.parent)
        loading.grab_set()
        center_window_on_screen(loading, 260, 100)
        ctk.CTkLabel(loading, text="Generating Invoice...",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        ctk.CTkProgressBar(loading, mode="indeterminate", width=200).pack(pady=5, padx=30)
        loading.update()

        def _generate():
            try:
                doc = SimpleDocTemplate(filename, pagesize=letter,
                                        topMargin=0.5*inch, bottomMargin=0.5*inch,
                                        leftMargin=0.6*inch, rightMargin=0.6*inch)
                styles = getSampleStyleSheet()
                story = []

                # --- Centered Company Header ---
                from reportlab.lib.styles import ParagraphStyle
                center_style = ParagraphStyle('Center', parent=styles['Normal'],
                                              alignment=1, spaceAfter=2)
                bold_center = ParagraphStyle('BoldCenter', parent=center_style,
                                             fontSize=18, leading=22, spaceAfter=2)
                addr_style = ParagraphStyle('Addr', parent=center_style,
                                            fontSize=9, leading=12, textColor=colors.HexColor('#555555'))
                contact_style = ParagraphStyle('Contact', parent=center_style,
                                               fontSize=9, leading=12, textColor=colors.HexColor('#777777'))

                header_elems = []

                if has_logo:
                    try:
                        img = Image(logo_path, width=1.2*inch, height=0.6*inch)
                        header_elems.append(img)
                        header_elems.append(Spacer(1, 4))
                    except Exception:
                        pass

                header_elems.append(Paragraph(company_name, bold_center))
                if company_address:
                    header_elems.append(Paragraph(company_address.replace('\n', '<br/>'), addr_style))
                contact_parts = []
                if company_phone:
                    contact_parts.append(f"Phone: {company_phone}")
                if company_email:
                    contact_parts.append(f"Email: {company_email}")
                if contact_parts:
                    header_elems.append(Paragraph(" | ".join(contact_parts), contact_style))

                for elem in header_elems:
                    story.append(elem)
                story.append(Spacer(1, 10))

                # --- Separator ---
                sep_style = TableStyle([('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a1a2e'))])
                sep_table = Table([[""]], colWidths=[6.3*inch])
                sep_table.setStyle(sep_style)
                story.append(sep_table)
                story.append(Spacer(1, 8))

                # --- Invoice Title ---
                title_style = ParagraphStyle('InvoiceTitle', parent=styles['Heading2'],
                                             textColor=colors.HexColor('#1a1a2e'),
                                             alignment=1, spaceBefore=0, spaceAfter=6)
                story.append(Paragraph("TAX INVOICE", title_style))
                story.append(Spacer(1, 6))

                # --- Invoice Details in bordered box ---
                detail_data = [
                    ["Invoice No.", invoice_number, "Date", selected_sale['sale_date']],
                    ["Customer", customer_name, "Payment", selected_sale['payment_method'].title()],
                    ["Status", selected_sale['status'].title(), "Amount", f"{currency} {selected_sale['total_amount']:.2f}"],
                ]
                detail_table = Table(detail_data,
                                    colWidths=[0.9*inch, 2.3*inch, 0.7*inch, 2.3*inch])
                detail_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
                    ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#555555')),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f8f8')),
                    ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#f8f8f8')),
                ]))
                story.append(detail_table)
                story.append(Spacer(1, 14))

                # --- Items Table ---
                items_header = ["#", "Product", "SKU", "Qty", "Unit Price", "Total"]
                items_data = [items_header]

                for i, item in enumerate(items, 1):
                    items_data.append([
                        str(i),
                        item['name'],
                        item['sku'],
                        str(item['quantity']),
                        f"{currency} {item['unit_price']:.2f}",
                        f"{currency} {item['total']:.2f}",
                    ])

                subtotal = selected_sale['total_amount'] + discount
                if discount > 0:
                    items_data.append(["", "", "", "", "Subtotal:", f"{currency} {subtotal:.2f}"])
                    items_data.append(["", "", "", "", "Discount:", f"-{currency} {discount:.2f}"])
                items_data.append(["", "", "", "", "Total:", f"{currency} {selected_sale['total_amount']:.2f}"])
                items_data.append(["", "", "", "", "Paid:", f"{currency} {selected_sale['paid_amount']:.2f}"])
                balance = selected_sale['total_amount'] - selected_sale['paid_amount']
                if balance > 0:
                    items_data.append(["", "", "", "", "Balance Due:", f"{currency} {balance:.2f}"])

                col_widths = [0.3*inch, 2.2*inch, 0.8*inch, 0.5*inch, 0.9*inch, 1*inch]
                items_table = Table(items_data, colWidths=col_widths, repeatRows=1)

                style_cmds = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (3, 0), (3, 0), 'CENTER'),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]

                summary_start = len(items_data) - (4 if balance > 0 else 3)
                if discount > 0:
                    summary_start -= 2
                if summary_start > 1:
                    style_cmds.append(('GRID', (0, 0), (-1, summary_start - 1), 0.5, colors.HexColor('#CBD5E1')))

                items_table.setStyle(TableStyle(style_cmds))

                for row_idx in range(summary_start, len(items_data)):
                    if row_idx >= 1:
                        cmds = [
                            ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, row_idx), (-1, row_idx), 10),
                        ]
                        if row_idx == summary_start:
                            cmds.append(('LINEABOVE', (0, row_idx), (-1, row_idx), 1, colors.HexColor('#1a1a2e')))
                        items_table.setStyle(TableStyle(cmds))

                story.append(items_table)
                story.append(Spacer(1, 20))

                # --- Footer ---
                story.append(Paragraph("Thank you for your business!", ParagraphStyle(
                    'ThankYou', parent=styles['Normal'], alignment=1,
                    fontSize=11, textColor=colors.HexColor('#888888'))))
                story.append(Spacer(1, 4))
                story.append(Paragraph(
                    f"Printed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    ParagraphStyle('PrintInfo', parent=styles['Normal'], alignment=1,
                                   fontSize=8, textColor=colors.HexColor('#aaaaaa'))))

                doc.build(story)
                self.parent.after(0, lambda: self._on_invoice_ready(loading, filename))
            except Exception as e:
                self.parent.after(0, lambda: self._on_invoice_error(loading, str(e)))

        _threading.Thread(target=_generate, daemon=True).start()

    def _on_invoice_ready(self, loading, filename):
        """Called when PDF generation succeeds."""
        try:
            loading.destroy()
        except Exception:
            pass
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Invoice Generated")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        center_window_on_screen(dialog, 380, 180)
        ctk.CTkLabel(dialog, text="✅ Invoice Generated Successfully",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#4CAF50").pack(pady=(25, 5))
        ctk.CTkLabel(dialog, text=os.path.basename(filename),
                     font=ctk.CTkFont(size=11)).pack(pady=2)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(15, 0))
        ctk.CTkButton(btn_frame, text="Open Invoice",
                       command=lambda: [dialog.destroy(), os.startfile(filename)],
                       width=120, height=35,
                       fg_color="#2563EB", hover_color="#1D4ED8").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close",
                       command=dialog.destroy,
                       width=100, height=35,
                       fg_color="#6B7280", hover_color="#4B5563").pack(side="left", padx=5)

    def _on_invoice_error(self, loading, error_msg):
        """Called when PDF generation fails."""
        try:
            loading.destroy()
        except Exception:
            pass
        messagebox.showerror("Error", f"Failed to generate invoice:\n{error_msg}")

    def ask_credit_paid_amount(self, total_amount):
        """Show a dialog asking how much the customer is paying now for a credit sale.
        Returns the paid amount (float), or None if the user cancelled."""
        dialog = CreditPaymentDialog(self.parent, total_amount)
        return dialog.result

    def process_sale(self):
        """Process the sale transaction"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        try:
            # Generate invoice number
            today = datetime.now()
            base_number = f"INV-{today.strftime('%Y%m%d')}"
            
            # Find next number for today
            query = "SELECT COUNT(*) as count FROM sales WHERE invoice_number LIKE ?"
            result = db.execute_query(query, (f"{base_number}-%",))
            count = result[0]['count'] if result else 0
            
            invoice_number = f"{base_number}-{count + 1:03d}"
            
            # Calculate totals
            customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
            subtotal = 0
            
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                subtotal += unit_price * item['quantity']
            
            # Calculate discount
            discount_amount = 0
            if self.discount_amount > 0 or self.discount_percentage > 0:
                if self.discount_type == "amount":
                    discount_amount = min(self.discount_amount, subtotal)
                else:  # percentage
                    discount_amount = (subtotal * self.discount_percentage) / 100
            
            total_amount = subtotal - discount_amount
            
            # Create sale record
            customer_id = self.current_customer['customer_id'] if self.current_customer else None
            payment_method = self.payment_var.get().lower()
            
            if payment_method == 'cash':
                paid_amount = total_amount
                status = 'completed'
            else:
                # Ask how much the customer is paying now (partial or full credit)
                paid_amount = self.ask_credit_paid_amount(total_amount)
                if paid_amount is None:
                    return  # User cancelled
                if paid_amount >= total_amount:
                    paid_amount = total_amount
                    status = 'completed'
                else:
                    status = 'credit'
            sale_id = db.execute_insert("""
                INSERT INTO sales (invoice_number, customer_id, sale_date, payment_method,
                                 subtotal, discount, total_amount, paid_amount, balance, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_number,
                customer_id,
                datetime.now().date(),
                payment_method,
                subtotal,
                discount_amount,
                total_amount,
                paid_amount,
                total_amount - paid_amount,
                status
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
                
                # Update stock
                db.execute_update("""
                    UPDATE products 
                    SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                """, (item['quantity'], item['product_id']))
            
            # Record sale transaction in payments table for complete history
            # Determine transaction type and notes based on payment status
            if payment_method == 'cash':
                # Cash sale - fully paid
                transaction_type = 'sale_cash'
                notes = f"Sale: Cash payment. Total: {total_amount:.2f}"
            elif status == 'completed':
                # Credit sale fully paid at time of purchase
                transaction_type = 'sale_credit_paid'
                notes = f"Sale: Credit fully paid. Total: {total_amount:.2f}"
            else:
                # Credit sale with balance remaining
                transaction_type = 'sale_credit'
                notes = f"Sale: Credit. Total: {total_amount:.2f}, Paid: {paid_amount:.2f}, Remaining: {total_amount - paid_amount:.2f}"
            
            db.execute_insert("""
                INSERT INTO payments (payment_type, customer_id, amount, 
                                    payment_method, reference_number, notes, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_type,
                customer_id,
                total_amount,  # Record the full sale amount
                payment_method,
                invoice_number,
                notes,
                datetime.now().date()
            ))
            
            # Record separate payment entry if there was an initial payment on credit sale
            if payment_method == 'credit' and paid_amount > 0:
                db.execute_insert("""
                    INSERT INTO payments (payment_type, customer_id, amount, 
                                        payment_method, reference_number, notes, payment_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    'payment',
                    customer_id,
                    paid_amount,
                    payment_method,
                    invoice_number,
                    f"Payment on invoice. Remaining: {total_amount - paid_amount:.2f}",
                    datetime.now().date()
                ))
            
            # Update customer credit balance if needed
            if payment_method == 'credit' and customer_id:
                db.execute_update("""
                    UPDATE customers 
                    SET credit_balance = credit_balance + ?
                    WHERE customer_id = ?
                """, (total_amount - paid_amount, customer_id))
            
            # Clear cart and refresh
            self.cart_items = []
            self.discount_amount = 0
            self.discount_type = "amount"
            self.discount_percentage = 0
            # Clear discount entry
            self.discount_entry.delete(0, tk.END)
            self.discount_type_var.set("amount")
            self.update_cart_display()
            self.load_products()
            
            messagebox.showinfo("Success", f"Sale completed successfully!\nInvoice: {invoice_number}")
            
        except Exception as e:
            print(f"Error processing sale: {e}")
            messagebox.showerror("Error", f"Failed to process sale: {e}")
    
    def apply_discount(self):
        """Open discount dialog and apply discount"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        # Calculate current subtotal
        subtotal = 0
        customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
        
        for item in self.cart_items:
            if customer_type == 'Workshop':
                unit_price = item['price_workshop']
            else:
                unit_price = item['price_normal']
            subtotal += unit_price * item['quantity']
        
        # Open discount dialog
        discount_dialog = DiscountDialog(self.parent, subtotal, self.discount_type, self.discount_amount, self.discount_percentage)
        
        if discount_dialog.result:
            self.discount_type = discount_dialog.discount_type
            self.discount_amount = discount_dialog.discount_amount
            self.discount_percentage = discount_dialog.discount_percentage
            self.update_cart_display()
            
            # Show confirmation message
            if self.discount_amount > 0 or self.discount_percentage > 0:
                if self.discount_type == "amount":
                    discount_text = f"Fixed discount of Rs{self.discount_amount:.2f} applied!"
                else:
                    discount_text = f"Percentage discount of {self.discount_percentage:.1f}% applied!"
                messagebox.showinfo("Discount Applied", discount_text)
            else:
                messagebox.showinfo("Discount Removed", "Discount has been removed from the cart.")
    
    def on_discount_type_change(self):
        """Handle discount type change in inline controls"""
        discount_type = self.discount_type_var.get()
        self.discount_type = discount_type
        
        # Update placeholder text
        if discount_type == "amount":
            self.discount_entry.configure(placeholder_text="Enter discount amount...")
        else:
            self.discount_entry.configure(placeholder_text="Enter discount percentage...")
        
        # Clear entry and reset discount
        self.discount_entry.delete(0, tk.END)
        self.discount_amount = 0
        self.discount_percentage = 0
        self.update_cart_display()
    
    def on_discount_change(self, event=None):
        """Handle discount entry changes for real-time preview"""
        # This method can be used for real-time preview if desired
        # For now, we'll keep it simple and only apply on button click
        pass
    
    def apply_inline_discount(self):
        """Apply discount from inline controls"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Add items first.")
            return
        
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            if discount_value < 0:
                messagebox.showerror("Error", "Discount value cannot be negative.")
                return
            
            if discount_value == 0:
                messagebox.showwarning("Warning", "Please enter a discount value greater than 0.")
                return
            
            # Calculate current subtotal for validation
            subtotal = 0
            customer_type = self.current_customer['type'] if self.current_customer else 'Normal'
            
            for item in self.cart_items:
                if customer_type == 'Workshop':
                    unit_price = item['price_workshop']
                else:
                    unit_price = item['price_normal']
                subtotal += unit_price * item['quantity']
            
            if discount_type == "amount":
                if discount_value > subtotal:
                    messagebox.showerror("Error", f"Discount amount cannot exceed subtotal (Rs{subtotal:.2f}).")
                    return
                self.discount_amount = discount_value
                self.discount_percentage = 0
            else:  # percentage
                if discount_value > 100:
                    messagebox.showerror("Error", "Discount percentage cannot exceed 100%.")
                    return
                self.discount_percentage = discount_value
                self.discount_amount = 0
            
            self.discount_type = discount_type
            self.update_cart_display()
            
            # Show success message
            if discount_type == "amount":
                messagebox.showinfo("Discount Applied", f"Fixed discount of Rs{discount_value:.2f} applied!")
            else:
                messagebox.showinfo("Discount Applied", f"Percentage discount of {discount_value:.1f}% applied!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid discount value.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def clear_inline_discount(self):
        """Clear discount from inline controls"""
        self.discount_amount = 0
        self.discount_percentage = 0
        self.discount_type = "amount"
        self.discount_entry.delete(0, tk.END)
        self.discount_type_var.set("amount")
        self.update_cart_display()


class CreditPaymentDialog:
    """Dialog to ask how much the customer is paying now on a credit sale."""
    def __init__(self, parent, total_amount):
        self.parent = parent
        self.total_amount = total_amount
        self.result = None  # None = cancelled, float = paid amount

        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("💳 Credit Sale - Payment Details")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog on screen
        center_window_on_screen(self.dialog, 420, 320)

        # Prevent closing with X without handling
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._build_ui()
        self.dialog.wait_window()

    def _build_ui(self):
        main = ctk.CTkFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main,
            text="💳 Credit Sale",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 5))

        # Total amount info
        info_frame = ctk.CTkFrame(main, fg_color=("#dbeafe", "#1e3a5f"))
        info_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            info_frame,
            text=f"Total Bill:  Rs{self.total_amount:.2f}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        # Amount paid now
        ctk.CTkLabel(
            main,
            text="Amount paid now by customer (Rs):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=5)

        self.paid_entry = ctk.CTkEntry(
            main,
            placeholder_text="Enter 0 for full credit, or partial amount...",
            font=ctk.CTkFont(size=13),
            height=38
        )
        self.paid_entry.insert(0, "0")
        self.paid_entry.pack(fill="x", padx=5, pady=(5, 5))
        self.paid_entry.bind("<KeyRelease>", self._update_preview)

        # Live preview label
        self.preview_label = ctk.CTkLabel(
            main,
            text=f"Credit remaining: Rs{self.total_amount:.2f}",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B35"
        )
        self.preview_label.pack(pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="✅ Confirm Sale",
            command=self.on_confirm,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", fill="x", expand=True)

        # Focus on entry
        self.paid_entry.focus()
        self.paid_entry.select_range(0, "end")

    def _update_preview(self, event=None):
        """Update the credit remaining preview as user types."""
        try:
            paid = float(self.paid_entry.get() or "0")
            paid = max(0, min(paid, self.total_amount))
            remaining = self.total_amount - paid
            if remaining <= 0:
                self.preview_label.configure(
                    text="✅ Fully paid — no credit remaining.",
                    text_color="#4CAF50"
                )
            else:
                self.preview_label.configure(
                    text=f"Credit remaining: Rs{remaining:.2f}",
                    text_color="#FF6B35"
                )
        except ValueError:
            self.preview_label.configure(
                text="⚠️ Enter a valid number.",
                text_color="#FF6B35"
            )

    def on_confirm(self):
        """Validate and confirm the paid amount."""
        try:
            paid = float(self.paid_entry.get() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the paid amount.", parent=self.dialog)
            return

        if paid < 0:
            messagebox.showerror("Invalid Input", "Paid amount cannot be negative.", parent=self.dialog)
            return

        if paid > self.total_amount:
            messagebox.showerror(
                "Invalid Input",
                f"Paid amount (Rs{paid:.2f}) cannot exceed the total bill (Rs{self.total_amount:.2f}).",
                parent=self.dialog
            )
            return

        self.result = paid
        self.dialog.destroy()

    def on_cancel(self):
        """User cancelled — result stays None."""
        self.result = None
        self.dialog.destroy()


class PaySaleCreditDialog:
    """Dialog to record a payment against a specific credit sale."""
    def __init__(self, parent, sale_data):
        self.parent = parent
        # Convert sqlite3.Row to dict if needed
        if hasattr(sale_data, 'keys') and callable(getattr(sale_data, 'keys', None)):
            self.sale_data = dict(sale_data)
        else:
            self.sale_data = sale_data
        self.balance = self.sale_data['total_amount'] - self.sale_data['paid_amount']
        self.result = False

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Pay Credit - {sale_data['invoice_number']}")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on screen
        center_window_on_screen(self.dialog, 460, 480)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self._build_ui()
        self.dialog.wait_window()

    def _build_ui(self):
        main = ctk.CTkFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main,
            text="💰 Pay Credit Balance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 10))

        # Invoice info box
        info_frame = ctk.CTkFrame(main, fg_color=("#fef3c7", "#3b2f00"))
        info_frame.pack(fill="x", pady=(0, 15))

        try:
            customer_name = self.sale_data['customer_name'] or "Walk-in Customer"
        except (KeyError, IndexError):
            customer_name = "Walk-in Customer"
        ctk.CTkLabel(
            info_frame,
            text=f"Invoice:   {self.sale_data['invoice_number']}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(
            info_frame,
            text=f"Customer: {customer_name}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(
            info_frame,
            text=f"Total Bill:    Rs{self.sale_data['total_amount']:.2f}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(
            info_frame,
            text=f"Already Paid: Rs{self.sale_data['paid_amount']:.2f}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=2)

        self.balance_label = ctk.CTkLabel(
            info_frame,
            text=f"Outstanding:  Rs{self.balance:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B35"
        )
        self.balance_label.pack(anchor="w", padx=15, pady=(2, 10))

        # Payment amount entry
        ctk.CTkLabel(
            main,
            text="Amount being paid now (Rs):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=5)

        self.pay_entry = ctk.CTkEntry(
            main,
            placeholder_text=f"Max: Rs{self.balance:.2f}",
            font=ctk.CTkFont(size=13),
            height=38
        )
        self.pay_entry.insert(0, f"{self.balance:.2f}")
        self.pay_entry.pack(fill="x", padx=5, pady=(5, 5))
        self.pay_entry.bind("<KeyRelease>", self._update_preview)

        # Live remaining label
        self.remaining_label = ctk.CTkLabel(
            main,
            text="After payment: Rs0.00 remaining",
            font=ctk.CTkFont(size=12),
            text_color="#4CAF50"
        )
        self.remaining_label.pack(pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="✅ Record Payment",
            command=self.on_confirm,
            height=38,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", fill="x", expand=True)

        self.pay_entry.focus()
        self.pay_entry.select_range(0, "end")
        self._update_preview()

    def _update_preview(self, event=None):
        try:
            paying = float(self.pay_entry.get() or "0")
            paying = max(0, min(paying, self.balance))
            remaining = self.balance - paying
            if remaining <= 0:
                self.remaining_label.configure(
                    text="✅ Fully paid after this payment!",
                    text_color="#4CAF50"
                )
            else:
                self.remaining_label.configure(
                    text=f"After payment: Rs{remaining:.2f} still remaining",
                    text_color="#FF6B35"
                )
        except ValueError:
            self.remaining_label.configure(
                text="⚠️ Enter a valid number.",
                text_color="#FF6B35"
            )

    def on_confirm(self):
        try:
            paying = float(self.pay_entry.get() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid payment amount.", parent=self.dialog)
            return

        if paying <= 0:
            messagebox.showerror("Invalid Input", "Payment amount must be greater than 0.", parent=self.dialog)
            return

        if paying > self.balance:
            messagebox.showerror(
                "Invalid Input",
                f"Payment (Rs{paying:.2f}) cannot exceed outstanding balance (Rs{self.balance:.2f}).",
                parent=self.dialog
            )
            return

        try:
            sale_id = self.sale_data['sale_id']
            new_paid = self.sale_data['paid_amount'] + paying
            new_balance = self.sale_data['total_amount'] - new_paid
            new_status = 'completed' if new_balance <= 0.01 else 'credit'

            # Update the sale record
            db.execute_update("""
                UPDATE sales
                SET paid_amount = ?, balance = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_paid, new_balance, new_status, sale_id))

            # Update customer credit balance if there is a customer
            customer_id = None
            sale_row = db.execute_query("SELECT customer_id FROM sales WHERE id = ?", (sale_id,))
            if sale_row:
                customer_id = sale_row[0]['customer_id']

            if customer_id:
                db.execute_update("""
                    UPDATE customers
                    SET credit_balance = credit_balance - ?
                    WHERE customer_id = ?
                """, (paying, customer_id))

            # Save a record in the payments table for history
            db.execute_insert("""
                INSERT INTO payments (payment_type, customer_id, amount, payment_method,
                                      reference_number, notes, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'sale_credit_payment',
                customer_id,
                paying,
                'cash',
                self.sale_data['invoice_number'],
                f"remaining:{new_balance:.2f}",
                datetime.now().strftime("%Y-%m-%d")
            ))

            if new_status == 'completed':
                messagebox.showinfo(
                    "Payment Recorded",
                    _fmt(paying) + f" recorded.\nInvoice {self.sale_data['invoice_number']} is now FULLY PAID!",
                    parent=self.dialog
                )
            else:
                messagebox.showinfo(
                    "Payment Recorded",
                    _fmt(paying) + f" recorded.\nRemaining balance: {_fmt(new_balance)}",
                    parent=self.dialog
                )

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            print(f"Error recording credit payment: {e}")
            messagebox.showerror("Error", f"Failed to record payment: {e}", parent=self.dialog)

    def on_cancel(self):
        self.result = False
        self.dialog.destroy()


class SaleDetailsDialog:
    def __init__(self, parent, sale_data):
        self.parent = parent
        # Convert sqlite3.Row to dict if needed
        if hasattr(sale_data, 'keys') and callable(getattr(sale_data, 'keys', None)):
            # It's already a dict-like object, ensure it's a real dict
            self.sale_data = dict(sale_data)
        else:
            self.sale_data = sale_data
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Sale Details - {sale_data['invoice_number']}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on screen
        center_window_on_screen(self.dialog, 600, 500)
        
        self.create_details_view()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_details_view(self):
        """Create the details view"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header information
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Invoice details
        invoice_label = ctk.CTkLabel(
            header_frame,
            text=f"Invoice: {self.sale_data['invoice_number']}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        invoice_label.pack(pady=10)
        
        details_frame = ctk.CTkFrame(header_frame)
        details_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Sale information
        discount_amount = self.sale_data['discount'] if 'discount' in self.sale_data.keys() else 0
        info_text = f"""
        Date: {self.sale_data['sale_date']}
        Customer: {self.sale_data['customer_name'] or 'Walk-in Customer'}
        Payment Method: {self.sale_data['payment_method'].title()}
        Status: {self.sale_data['status'].title()}
        Discount Applied: Rs{discount_amount:.2f}{' (None)' if discount_amount == 0 else ''}
        Total Amount: Rs{self.sale_data['total_amount']:.2f}
        """
        
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=10)
        
        # Sale items
        items_label = ctk.CTkLabel(
            main_frame,
            text="Sale Items:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        items_label.pack(anchor="w", pady=(0, 10))
        
        # Items table
        items_frame = ctk.CTkFrame(main_frame)
        items_frame.pack(fill="both", expand=True)
        
        # Load and display sale items
        self.load_sale_items(items_frame)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.dialog.destroy,
            width=100,
            height=35
        )
        close_btn.pack(pady=(20, 0))
    
    def load_sale_items(self, parent):
        """Load and display sale items"""
        try:
            query = """
                SELECT si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """
            items = db.execute_query(query, (self.sale_data['sale_id'],))
            
            # Create treeview for items with enhanced styling
            columns = ("SKU", "Product", "Quantity", "Unit Price", "Total")
            items_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
            
            # Apply centralized styling
            table_styles.apply_sale_details_style(items_tree)
            
            # Define headings and column widths - bigger columns
            column_widths = {"SKU": 120, "Product": 220, "Quantity": 100, 
                           "Unit Price": 120, "Total": 120}
            
            for col in columns:
                items_tree.heading(col, text=f"  {col}  ", anchor="center")
                items_tree.column(col, width=column_widths.get(col, 120), anchor="center" if col != "Product" else "w", minwidth=80)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=items_tree.yview)
            items_tree.configure(yscrollcommand=v_scrollbar.set)
            
            # Pack table and scrollbar
            items_tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            
            # Add items to tree
            for item in items:
                items_tree.insert("", "end", values=(
                    item['sku'],
                    item['name'],
                    item['quantity'],
                _fmt(item['unit_price']),
                _fmt(item['total'])
                ))
                
        except Exception as e:
            print(f"Error loading sale items: {e}")
            error_label = ctk.CTkLabel(
                parent,
                text="Error loading sale items",
                font=ctk.CTkFont(size=12)
            )
            error_label.pack(pady=20)


class DiscountDialog:
    def __init__(self, parent, subtotal, current_discount_type="amount", current_discount_amount=0, current_discount_percentage=0):
        self.parent = parent
        self.subtotal = subtotal
        self.discount_type = current_discount_type
        self.discount_amount = current_discount_amount
        self.discount_percentage = current_discount_percentage
        self.result = False
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Apply Discount")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on screen
        center_window_on_screen(self.dialog, 750, 600)
        
        # Make dialog resizable
        self.dialog.minsize(450, 400)
        
        # Prevent closing with X button without handling
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_discount_interface()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_discount_interface(self):
        """Create the discount interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="💸 Apply Discount",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Current subtotal display
        subtotal_frame = ctk.CTkFrame(main_frame)
        subtotal_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            subtotal_frame,
            text=f"Current Subtotal: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Discount type selection
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            type_frame,
            text="Discount Type:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Radio buttons for discount type
        self.discount_type_var = tk.StringVar(value=self.discount_type)
        
        amount_radio = ctk.CTkRadioButton(
            type_frame,
            text="Fixed Amount (Rs)",
            variable=self.discount_type_var,
            value="amount",
            command=self.on_discount_type_changed
        )
        amount_radio.pack(anchor="w", padx=30, pady=5)
        
        percentage_radio = ctk.CTkRadioButton(
            type_frame,
            text="Percentage (%)",
            variable=self.discount_type_var,
            value="percentage",
            command=self.on_discount_type_changed
        )
        percentage_radio.pack(anchor="w", padx=30, pady=(5, 10))
        
        # Discount value input
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=(0, 15))
        
        self.discount_label = ctk.CTkLabel(
            input_frame,
            text="Discount Amount (Rs):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.discount_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.discount_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter discount value...",
            font=ctk.CTkFont(size=12)
        )
        self.discount_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Set initial values
        if self.discount_type == "amount" and self.discount_amount > 0:
            self.discount_entry.insert(0, str(self.discount_amount))
        elif self.discount_type == "percentage" and self.discount_percentage > 0:
            self.discount_entry.insert(0, str(self.discount_percentage))
        
        # Bind entry changes to update preview
        self.discount_entry.bind('<KeyRelease>', self.update_preview)
        
        # Preview section
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            preview_frame,
            text="Preview:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.preview_subtotal = ctk.CTkLabel(
            preview_frame,
            text=f"Subtotal: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=12)
        )
        self.preview_subtotal.pack(anchor="w", padx=30, pady=2)
        
        self.preview_discount = ctk.CTkLabel(
            preview_frame,
            text="Discount: Rs0.00",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B35"
        )
        self.preview_discount.pack(anchor="w", padx=30, pady=2)
        
        self.preview_total = ctk.CTkLabel(
            preview_frame,
            text=f"Final Total: Rs{self.subtotal:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        )
        self.preview_total.pack(anchor="w", padx=30, pady=(2, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Create a grid layout for better button spacing
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.on_cancel,
            width=110,
            height=40,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cancel_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Remove Discount",
            command=self.on_clear,
            width=140,
            height=40,
            fg_color="#FF6B35",
            hover_color="#E55A2B",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        clear_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="✅ Apply Discount",
            command=self.on_apply,
            width=130,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        apply_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        # Update interface based on current type
        self.on_discount_type_changed()
        self.update_preview()
    
    def on_discount_type_changed(self):
        """Handle discount type change"""
        discount_type = self.discount_type_var.get()
        
        if discount_type == "amount":
            self.discount_label.configure(text="Discount Amount (Rs):")
            self.discount_entry.configure(placeholder_text="Enter amount...")
        else:
            self.discount_label.configure(text="Discount Percentage (%):")
            self.discount_entry.configure(placeholder_text="Enter percentage...")
        
        # Clear entry when switching types
        if discount_type != self.discount_type:
            self.discount_entry.delete(0, tk.END)
        
        self.discount_type = discount_type
        self.update_preview()
    
    def update_preview(self, event=None):
        """Update the discount preview"""
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            if discount_type == "amount":
                discount_amount = min(discount_value, self.subtotal)  # Can't discount more than subtotal
                discount_text = f"Discount: -Rs{discount_amount:.2f}"
            else:  # percentage
                discount_percentage = min(discount_value, 100)  # Max 100%
                discount_amount = (self.subtotal * discount_percentage) / 100
                discount_text = f"Discount ({discount_percentage:.1f}%): -Rs{discount_amount:.2f}"
            
            final_total = self.subtotal - discount_amount
            
            self.preview_discount.configure(text=discount_text)
            self.preview_total.configure(text=f"Final Total: Rs{final_total:.2f}")
            
        except ValueError:
            # Invalid input
            self.preview_discount.configure(text="Discount: Rs0.00")
            self.preview_total.configure(text=f"Final Total: Rs{self.subtotal:.2f}")
    
    def on_apply(self):
        """Apply the discount"""
        try:
            discount_value = float(self.discount_entry.get() or "0")
            discount_type = self.discount_type_var.get()
            
            if discount_value < 0:
                messagebox.showerror("Error", "Discount value cannot be negative.")
                return
            
            if discount_type == "amount":
                if discount_value > self.subtotal:
                    messagebox.showerror("Error", f"Discount amount cannot exceed subtotal (Rs{self.subtotal:.2f}).")
                    return
                self.discount_amount = discount_value
                self.discount_percentage = 0
            else:  # percentage
                if discount_value > 100:
                    messagebox.showerror("Error", "Discount percentage cannot exceed 100%.")
                    return
                self.discount_percentage = discount_value
                self.discount_amount = (self.subtotal * discount_value) / 100
            
            self.discount_type = discount_type
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid discount value.")
    
    def on_clear(self):
        """Remove discount"""
        self.discount_amount = 0
        self.discount_percentage = 0
        self.discount_type = "amount"
        self.result = True
        self.dialog.destroy()
    
    def on_cancel(self):
        """Cancel discount dialog"""
        self.result = False
        self.dialog.destroy()
