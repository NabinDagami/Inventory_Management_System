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
        self.create_sales_interface()
        self.load_customers()
        self.load_products()

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
        self._hide_search_dropdown()
        # Close any floating overrideredirect Toplevel popups
        root = self.parent.winfo_toplevel()
        for w in root.winfo_children():
            if isinstance(w, tk.Toplevel) and w.winfo_exists():
                try:
                    if w.overrideredirect():
                        w.destroy()
                except Exception:
                    pass
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

        # Customer info display
        self.customer_info_frame = ctk.CTkFrame(self.new_sale_frame, fg_color="transparent")
        self.customer_info_frame.pack(fill="x", padx=10, pady=(0, 5))

        info_inner = ctk.CTkFrame(self.customer_info_frame, fg_color=("#F8FAFC", "#1E293B"))
        info_inner.pack(fill="x", padx=0, pady=0, ipady=2)

        ctk.CTkLabel(info_inner, text="Name:", font=ctk.CTkFont(size=10), text_color=("gray50", "gray60")).pack(side="left", padx=(10, 3))
        self.customer_name_val = ctk.CTkLabel(info_inner, text="Walk-in Customer", font=ctk.CTkFont(size=10, weight="bold"))
        self.customer_name_val.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(info_inner, text="Phone:", font=ctk.CTkFont(size=10), text_color=("gray50", "gray60")).pack(side="left", padx=(0, 3))
        self.customer_phone_val = ctk.CTkLabel(info_inner, text="N/A", font=ctk.CTkFont(size=10, weight="bold"))
        self.customer_phone_val.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(info_inner, text="Credit:", font=ctk.CTkFont(size=10), text_color=("gray50", "gray60")).pack(side="left", padx=(0, 3))
        self.customer_credit_val = ctk.CTkLabel(info_inner, text="Rs 0.00", font=ctk.CTkFont(size=10, weight="bold"))
        self.customer_credit_val.pack(side="left", padx=(0, 12))
        
        # Content area — single-column layout (cart lives inside product frame)
        content_frame = ctk.CTkFrame(self.new_sale_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Full-width — Product selection + Cart
        self.create_product_selection(content_frame)
    
    def create_sales_history_interface(self):
        """Create the sales history interface"""
        self.sales_history_frame = ctk.CTkFrame(self.content_container)
        
        # Header with search and filters
        header_frame = ctk.CTkFrame(self.sales_history_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(header_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color=("#334155", "#F8FAFC"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.sales_search_var = ctk.StringVar()
        self.sales_search_var.trace('w', self.filter_sales_history)
        search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.sales_search_var,
            placeholder_text="Search by invoice number or customer...",
            width=300,
            fg_color=("#FFFFFF", "#334155"),
            text_color=("#1E293B", "#F8FAFC"),
            placeholder_text_color=("#94A3B8", "#64748B")
        )
        search_entry.pack(side="left", padx=5, pady=10)

        # Status filter dropdown
        status_label = ctk.CTkLabel(header_frame, text="Status:", font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color=("#334155", "#F8FAFC"))
        status_label.pack(side="left", padx=(10, 5), pady=10)

        self.sales_status_filter = ctk.StringVar(value="All")
        status_dropdown = ctk.CTkOptionMenu(
            header_frame,
            variable=self.sales_status_filter,
            values=["All", "Completed", "Credit"],
            width=140,
            command=lambda _: self.filter_sales_history(),
            fg_color=("#FFFFFF", "#334155"),
            text_color=("#1E293B", "#F8FAFC"),
            button_color=("#E2E8F0", "#475569"),
            button_hover_color=("#CBD5E1", "#64748B")
        )
        status_dropdown.pack(side="left", padx=5, pady=10)

        # Customer filter dropdown
        customer_label = ctk.CTkLabel(header_frame, text="Customer:", font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color=("#334155", "#F8FAFC"))
        customer_label.pack(side="left", padx=(10, 5), pady=10)

        self.sales_customer_filter = ctk.StringVar(value="All")
        self.sales_customer_dropdown = ctk.CTkOptionMenu(
            header_frame,
            variable=self.sales_customer_filter,
            values=["All"],
            width=160,
            command=lambda _: self.filter_sales_history(),
            fg_color=("#FFFFFF", "#334155"),
            text_color=("#1E293B", "#F8FAFC"),
            button_color=("#E2E8F0", "#475569"),
            button_hover_color=("#CBD5E1", "#64748B")
        )
        self.sales_customer_dropdown.pack(side="left", padx=5, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_sales_history,
            width=100,
            height=35,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Sales history table - fixed max height so it doesn't stretch
        table_frame = ctk.CTkFrame(self.sales_history_frame, height=450)
        table_frame.pack(fill="both", padx=10, pady=0)
        table_frame.pack_propagate(False)
        
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
        
        # Action buttons at bottom (always visible)
        actions_frame = ctk.CTkFrame(self.sales_history_frame)
        actions_frame.pack(fill="x", side="bottom", pady=(10, 10), padx=10)

        self.history_view_btn = ctk.CTkButton(
            actions_frame,
            text="View Details",
            command=self.view_sale_details,
            width=120, height=35,
            state="disabled",
            fg_color="#3b82f6", hover_color="#2563eb",
            text_color="#FFFFFF",
            text_color_disabled="#9CA3AF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold")
        )
        self.history_view_btn.pack(side="left", padx=5)

        self.history_pay_btn = ctk.CTkButton(
            actions_frame,
            text="Pay Credit",
            command=self.pay_credit_for_sale,
            width=120, height=35,
            state="disabled",
            fg_color="#10b981", hover_color="#059669",
            text_color="#FFFFFF",
            text_color_disabled="#9CA3AF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold")
        )
        self.history_pay_btn.pack(side="left", padx=5)

        self.history_export_btn = ctk.CTkButton(
            actions_frame,
            text="Export Invoice",
            command=self.export_invoice,
            width=120, height=35,
            state="disabled",
            fg_color="#8b5cf6", hover_color="#7c3aed",
            text_color="#FFFFFF",
            text_color_disabled="#9CA3AF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold")
        )
        self.history_export_btn.pack(side="left", padx=5)

        self.history_print_btn = ctk.CTkButton(
            actions_frame,
            text="Print Bill",
            command=self.print_invoice,
            width=120, height=35,
            state="disabled",
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#FFFFFF",
            text_color_disabled="#9CA3AF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold")
        )
        self.history_print_btn.pack(side="left", padx=5)

        # Track selection changes to enable/disable buttons
        self.sales_history_tree.bind("<<TreeviewSelect>>", self._on_history_select)
        # Double-click to view details
        self.sales_history_tree.bind("<Double-1>", lambda e: self.view_sale_details())
    
    def _on_history_select(self, event=None):
        """Enable/disable action buttons based on treeview selection."""
        sel = self.sales_history_tree.selection()
        enabled = len(sel) > 0
        state = "normal" if enabled else "disabled"
        self.history_view_btn.configure(state=state)
        self.history_pay_btn.configure(state=state)
        self.history_export_btn.configure(state=state)
        self.history_print_btn.configure(state=state)

    def load_sales_history(self):
        """Load sales history data"""
        try:
            query = """
                SELECT s.id as sale_id, s.invoice_number, s.sale_date, s.payment_method,
                       s.total_amount, s.paid_amount, (s.total_amount - s.paid_amount) as credit,
                       s.discount, s.status, s.notes, c.name as customer_name,
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

                # Check if there are returns from notes
                notes = sale.get('notes') or ""
                has_returns = any(line.strip().startswith('[Return]') for line in notes.split('\n'))
                status_display = status
                if has_returns:
                    # Count total returned items
                    ret_count = 0
                    for line in notes.split('\n'):
                        if line.strip().startswith('[Return]') and 'items=' in line:
                            try:
                                import json
                                items_part = line.split('items=')[1].split(' refund=')[0]
                                items_data = json.loads(items_part.replace("'", '"'))
                                ret_count += sum(items_data.values())
                            except Exception:
                                pass
                    if ret_count > 0:
                        status_display = f"↩{ret_count} {status}"
                
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
                    status_display
                ))
            
            self.all_sales_data = sales

            # Populate customer filter dropdown
            customers = sorted(set(
                (sale['customer_name'] or "Walk-in Customer") for sale in sales
            ))
            self.sales_customer_dropdown.configure(values=["All"] + customers)

        except Exception as e:
            print(f"Error loading sales history: {e}")
            messagebox.showerror("Error", f"Failed to load sales history: {e}")
    
    def filter_sales_history(self, *args):
        """Filter sales history based on search, status and customer"""
        search_term = self.sales_search_var.get().lower()
        status_filter = self.sales_status_filter.get()
        customer_filter = self.sales_customer_filter.get()

        # Clear tree
        for item in self.sales_history_tree.get_children():
            self.sales_history_tree.delete(item)

        if not hasattr(self, 'all_sales_data'):
            return

        # Filter and display matching sales
        for idx, sale in enumerate(self.all_sales_data):
            customer_name = sale['customer_name'] or "Walk-in Customer"

            # Apply search filter
            if search_term:
                if (search_term not in sale['invoice_number'].lower() and
                    search_term not in customer_name.lower()):
                    continue

            # Apply status filter
            if status_filter != "All":
                sale_status = (sale.get('status') or "").lower()
                filter_status = status_filter.lower().replace(" ", "_")
                if sale_status != filter_status:
                    continue

            # Apply customer filter
            if customer_filter != "All" and customer_name != customer_filter:
                continue

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
        dialog = SaleDetailsDialog(self.parent, selected_sale, self.load_sales_history)
    
    def create_product_selection(self, parent):
        """Create product selection area with search, barcode, Browse button + modal"""
        product_frame = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"), corner_radius=6)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        product_frame.grid_rowconfigure(2, weight=1)
        product_frame.grid_columnconfigure(0, weight=1)
        self.product_frame = product_frame

        # Row 0: Title
        ctk.CTkLabel(
            product_frame, text="📦 Select Products",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

        # Row 1: Search + Barcode + Browse Products
        search_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=(4, 4))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="Search products...",
            height=32
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        self.search_entry.bind("<KeyRelease>", self._on_search_keyrelease)
        self.search_entry.bind("<Return>", self._on_search_enter)
        self.search_entry.bind("<Escape>", lambda e: self._hide_search_dropdown())
        self.search_entry.bind("<Down>", self._on_search_arrow_down)

        # Browse Products button — immediately after search entry
        self.browse_btn = ctk.CTkButton(
            search_frame,
            text="📦  Browse Products",
            command=lambda: self._open_product_browser(self.search_var.get()),
            font=ctk.CTkFont(size=12),
            height=35,
            width=150,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=6
        )
        self.browse_btn.grid(row=0, column=2, padx=(0, 8))

        ctk.CTkLabel(search_frame, text="📷", font=ctk.CTkFont(size=13)).grid(row=0, column=3, padx=(4, 4))

        self.barcode_var = ctk.StringVar()
        self.barcode_entry = ctk.CTkEntry(
            search_frame, textvariable=self.barcode_var,
            placeholder_text="Scan barcode...",
            width=130, height=32
        )
        self.barcode_entry.grid(row=0, column=4, padx=(0, 2))
        self.barcode_entry.bind("<Return>", self._on_barcode_scanned)

        self.barcode_status = ctk.CTkLabel(
            search_frame, text="", font=ctk.CTkFont(size=11),
            anchor="w", width=110
        )
        self.barcode_status.grid(row=0, column=5, padx=(0, 4))

        # Search dropdown overlay (hidden by default)
        self._search_dropdown = None
        self._tooltip = None

        # === Row 2: Cart section (fills remaining space) ===
        self._build_cart_in_product(product_frame)

    # ── Cart embedded in product frame ──────────────────────────────

    def _build_cart_in_product(self, parent):
        """Build the shopping cart inside the product selection frame."""
        cart_outer = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"),
                                   border_width=1, border_color=("#CBD5E1", "#334155"),
                                   corner_radius=6)
        cart_outer.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 8))
        cart_outer.grid_rowconfigure(1, weight=1)
        cart_outer.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(cart_outer, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 2))
        ctk.CTkLabel(header_frame, text="🛒 Shopping Cart",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.cart_badge = ctk.CTkLabel(
            header_frame, text="(0)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white", fg_color="#3b82f6",
            corner_radius=8, padx=8, pady=2
        )
        self.cart_badge.pack(side="left", padx=(8, 0))

        # Scrollable body — items, discount, totals, proceed
        self.cart_scroll_body = ctk.CTkScrollableFrame(cart_outer, fg_color="transparent")
        self.cart_scroll_body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Items container
        cart_table_frame = ctk.CTkFrame(self.cart_scroll_body, fg_color="transparent")
        cart_table_frame.pack(fill="x", padx=10, pady=(5, 8))

        self.cart_items_container = ctk.CTkFrame(cart_table_frame, fg_color=("#FFFFFF", "#1E1E2E"), height=200)
        self.cart_items_container.pack(fill="x", expand=False, padx=2, pady=2)

        # Centered empty-state label
        self.cart_empty_label = ctk.CTkLabel(
            self.cart_items_container,
            text="No items in cart. Search or browse products to add.",
            font=ctk.CTkFont(size=11),
            text_color=("#94A3B8", "#64748B"),
        )
        self.cart_empty_label.place(relx=0.5, rely=0.5, anchor="center")

        # Column headers
        self.cart_header_frame = ctk.CTkFrame(cart_table_frame, fg_color=("#F1F5F9", "#0F172A"), height=28)
        self.cart_header_frame.pack(fill="x", padx=2, pady=(0, 2))
        self.cart_header_frame.pack_propagate(False)
        ctk.CTkLabel(self.cart_header_frame, text="Product", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(self.cart_header_frame, text="Qty", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="left", padx=(50, 0))
        ctk.CTkLabel(self.cart_header_frame, text="Price", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="right", padx=(0, 60))
        ctk.CTkLabel(self.cart_header_frame, text="Total", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).pack(side="right", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            cart_table_frame, text="🗑 Clear Cart",
            command=self.clear_cart, width=85, height=22,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=("#E2E8F0", "#334155"),
            text_color=("#475569", "#94A3B8"),
            hover_color=("#CBD5E1", "#475569")
        )
        clear_btn.pack(anchor="e", pady=(3, 0))

        # Discount section
        discount_frame = ctk.CTkFrame(self.cart_scroll_body, fg_color="transparent")
        discount_frame.pack(fill="x", padx=8, pady=(5, 5))
        ctk.CTkLabel(discount_frame, text="💸 Discount",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 3))

        quick_pct_frame = ctk.CTkFrame(discount_frame, fg_color="transparent")
        quick_pct_frame.pack(fill="x", padx=8, pady=(0, 5))
        for pct, color in [("5%", "#059669"), ("10%", "#0284c7"), ("15%", "#7c3aed"), ("20%", "#dc2626")]:
            btn = ctk.CTkButton(quick_pct_frame, text=pct, width=45, height=26,
                                font=ctk.CTkFont(size=10, weight="bold"),
                                fg_color=color, hover_color=color,
                                command=lambda v=pct: self._quick_discount_percentage(v))
            btn.pack(side="left", padx=(0, 4))
        ctk.CTkButton(quick_pct_frame, text="Clear", width=45, height=26,
                       font=ctk.CTkFont(size=10, weight="bold"),
                       fg_color="#6B7280", hover_color="#4B5563",
                       command=self.clear_inline_discount).pack(side="left")

        discount_type_frame = ctk.CTkFrame(discount_frame, fg_color="transparent")
        discount_type_frame.pack(fill="x", padx=8, pady=(0, 3))
        self.discount_type_var = tk.StringVar(value="amount")
        ctk.CTkRadioButton(discount_type_frame, text="Amount (Rs)",
                            variable=self.discount_type_var, value="amount",
                            command=self.on_discount_type_change,
                            font=ctk.CTkFont(size=11)).pack(side="left", padx=(8, 15))
        ctk.CTkRadioButton(discount_type_frame, text="Percentage (%)",
                            variable=self.discount_type_var, value="percentage",
                            command=self.on_discount_type_change,
                            font=ctk.CTkFont(size=11)).pack(side="left")

        discount_input_frame = ctk.CTkFrame(discount_frame, fg_color="transparent")
        discount_input_frame.pack(fill="x", padx=8, pady=(0, 5))
        self.discount_entry = ctk.CTkEntry(discount_input_frame,
                                            placeholder_text="Enter discount...",
                                            width=120, height=28,
                                            font=ctk.CTkFont(size=11))
        self.discount_entry.pack(side="left", padx=(8, 5), pady=5)
        self.discount_entry.bind('<KeyRelease>', self.on_discount_change)
        ctk.CTkButton(discount_input_frame, text="Apply",
                       command=self.apply_inline_discount,
                       width=50, height=28,
                       font=ctk.CTkFont(size=11, weight="bold"),
                       fg_color="#FF6B35", hover_color="#E55A2B"
                       ).pack(side="left")

        # Summary
        summary_frame = ctk.CTkFrame(self.cart_scroll_body, fg_color=("#F0FDF4", "#0F172A"))
        summary_frame.pack(fill="x", padx=8, pady=(5, 8))
        inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        def _summary_row(parent, label, attr, color=None):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", pady=(0, 2))
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12)).pack(side="left")
            v = ctk.CTkLabel(r, text=_fmt(0), font=ctk.CTkFont(size=12, weight="bold"),
                              anchor="e", text_color=color or ("gray10", "gray90"))
            v.pack(side="right")
            return v

        self.subtotal_value = _summary_row(inner, "Subtotal", "subtotal")
        self.discount_value = _summary_row(inner, "Discount", "discount", "#FF6B35")
        ctk.CTkFrame(inner, height=1, fg_color=("#CBD5E1", "#334155")).pack(fill="x", pady=4)

        total_row = ctk.CTkFrame(inner, fg_color="transparent")
        total_row.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(total_row, text="GRAND TOTAL", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.total_value = ctk.CTkLabel(total_row, text="Rs 0.00",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color="#10b981", anchor="e")
        self.total_value.pack(side="right")

        # Proceed button
        self.proceed_btn = ctk.CTkButton(
            self.cart_scroll_body,
            text="Proceed Sale - Rs 0.00",
            command=self._on_proceed_sale,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            state="disabled",
            fg_color="#374151",
            text_color="#9CA3AF",
            hover_color="#374151"
        )
        self.proceed_btn.pack(fill="x", padx=8, pady=(5, 12))

    # ── Search Dropdown ──────────────────────────────────────────────

    def _show_search_dropdown(self, matches):
        """Show a CTkFrame dropdown below the search entry using place()."""
        self._hide_search_dropdown()
        if not matches or not hasattr(self, 'search_entry') or not self.search_entry.winfo_exists():
            return

        pf = self.product_frame
        pf.update_idletasks()
        rel_x = self.search_entry.winfo_rootx() - pf.winfo_rootx()
        rel_y = self.search_entry.winfo_rooty() - pf.winfo_rooty() + self.search_entry.winfo_height() + 4

        w = int(self.search_entry.winfo_width() * 0.75)
        w = max(w, 400)
        w = min(w, 800)

        if rel_x + w > pf.winfo_width():
            rel_x = pf.winfo_width() - w - 10

        pf_h = pf.winfo_height()
        max_h = max(pf_h - rel_y - 10, 80)
        desired = len(matches) * 34 + 10
        h = max(min(desired, max_h, 400), min(250, desired))

        self._search_dropdown = ctk.CTkFrame(
            pf, fg_color="#1f2937", corner_radius=6,
            border_width=1, border_color="#4B5563",
            width=w, height=h
        )
        self._search_dropdown.place(x=rel_x, y=rel_y, anchor="nw")
        self._search_dropdown.update_idletasks()

        inner = ctk.CTkScrollableFrame(self._search_dropdown, fg_color="#1f2937",
                                        scrollbar_button_hover_color="#4B5563",
                                        corner_radius=0,
                                        width=w)
        inner.pack(fill="both", expand=True)

        # Available width for text
        btn_w = w - 50

        for p in matches:
            avail = self.get_available_stock(p)
            stock_part = f"  —  Stock: {avail}" if avail > 0 else "  —  Out of Stock"
            name = p['name']
            full_label = f"{name}{stock_part}"

            # Truncate name if the full label won't fit
            est_w = len(full_label) * 7
            display = full_label
            if est_w > btn_w:
                max_name_chars = max((btn_w - len(stock_part) * 7) // 7 - 3, 10)
                display = f"{name[:max_name_chars]}...{stock_part}"

            row = ctk.CTkFrame(inner, fg_color="transparent", height=34)
            row.pack(fill="x", padx=6, pady=1)
            row.pack_propagate(False)

            lbl = ctk.CTkLabel(
                row, text=display,
                anchor="w", justify="left",
                font=ctk.CTkFont(size=12),
                text_color="#F8FAFC",
                padx=12
            )
            lbl.pack(side="left", fill="x", expand=True)

            prod = p
            def _on_row_enter(event, r=row):
                r.configure(fg_color="#374151")
            def _on_row_leave(event, r=row):
                r.configure(fg_color="transparent")
            def _on_row_click(event, prod=prod):
                self._search_dropdown_add(prod)
                return "break"

            row.bind("<Enter>", _on_row_enter)
            row.bind("<Leave>", _on_row_leave)
            lbl.bind("<Enter>", _on_row_enter)
            lbl.bind("<Leave>", _on_row_leave)
            row.bind("<Button-1>", _on_row_click)
            lbl.bind("<Button-1>", _on_row_click)

        inner.configure(width=w)
        self._search_dropdown.configure(width=w, height=h)
        self._search_dropdown.lift()
        self._bind_dropdown_close()

    def _show_tooltip(self, event, text):
        """Show a tooltip with the full product name on hover."""
        self._hide_tooltip()
        pf = self.product_frame
        tip = ctk.CTkFrame(pf, fg_color="#1e293b", corner_radius=4,
                           border_width=1, border_color="#4B5563")
        # Position near cursor, relative to product_frame
        x = event.x_root - pf.winfo_rootx() + 12
        y = event.y_root - pf.winfo_rooty() + 12
        tip.place(x=x, y=y, anchor="nw")
        lbl = ctk.CTkLabel(tip, text=text, text_color="#F8FAFC",
                            font=ctk.CTkFont(size=11), padx=10, pady=4)
        lbl.pack()
        tip.update_idletasks()
        self._tooltip = tip

    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self._tooltip:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
            self._tooltip = None

        if self._search_dropdown:
            self._search_dropdown.destroy()
            self._search_dropdown = None

    def _search_dropdown_add(self, product):
        """Add the selected product from the dropdown and clean up."""
        self.add_to_cart(quantity=1, product=product)
        self.search_var.set("")
        self._hide_search_dropdown()
        self.search_entry.focus_set()

    def _hide_search_dropdown(self):
        """Hide the search dropdown."""
        self._hide_tooltip()
        if self._search_dropdown:
            try:
                self._search_dropdown.place_forget()
                self._search_dropdown.destroy()
            except Exception:
                pass
            self._search_dropdown = None
        try:
            self.product_frame.unbind("<Button-1>", self._dropdown_close_id)
        except Exception:
            pass

    def _bind_dropdown_close(self):
        """Bind a click-outside handler to close the dropdown."""
        try:
            self.product_frame.unbind("<Button-1>", self._dropdown_close_id)
        except Exception:
            pass
        self._dropdown_close_id = self.product_frame.bind(
            "<Button-1>", self._on_dropdown_outside_click, add="+"
        )

    def _on_dropdown_outside_click(self, event):
        """Close the search dropdown when clicking outside it."""
        if not self._search_dropdown or not self._search_dropdown.winfo_exists():
            return
        try:
            dx = self._search_dropdown.winfo_rootx()
            dy = self._search_dropdown.winfo_rooty()
            dw = self._search_dropdown.winfo_width()
            dh = self._search_dropdown.winfo_height()
        except Exception:
            return
        if dw <= 0 or dh <= 0:
            return
        if (dx <= event.x_root <= dx + dw and dy <= event.y_root <= dy + dh):
            return
        try:
            sx = self.search_entry.winfo_rootx()
            sy = self.search_entry.winfo_rooty()
            sw = self.search_entry.winfo_width()
            sh = self.search_entry.winfo_height()
        except Exception:
            sw = sh = 0
        if sw > 0 and sh > 0 and (sx <= event.x_root <= sx + sw and sy <= event.y_root <= sy + sh):
            return
        self._hide_search_dropdown()

    def _on_search_keyrelease(self, event=None):
        """Handle typing in the search entry — show dropdown with matches."""
        if event and event.keysym in ("Down", "Up", "Return", "Escape"):
            return
        term = self.search_var.get().strip()
        if not term or len(term) < 1:
            self._hide_search_dropdown()
            return
        matches = [
            p for p in self.all_products
            if term in p['name'].lower() or term in p['sku'].lower()
        ][:8]
        self._show_search_dropdown(matches)

    def _on_search_enter(self, event=None):
        """Enter key — add first search result or open browse modal."""
        term = self.search_var.get().strip()
        if not term:
            self._hide_search_dropdown()
            self._open_product_browser()
            return
        # Try to find first match
        for p in self.all_products:
            if term.lower() in p['name'].lower() or term.lower() in p['sku'].lower():
                self._hide_search_dropdown()
                self._search_dropdown_add(p)
                return
        # No match — open modal
        self._hide_search_dropdown()
        self._open_product_browser(term)

    def _on_search_arrow_down(self, event=None):
        pass

    def _open_product_browser(self, initial_search=""):
        """Open a modal window to browse and select products."""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Select Products")
        modal.geometry("900x600")
        modal.minsize(600, 400)
        modal.transient(self.parent)
        modal.grab_set()
        modal.resizable(True, True)

        # ── Header ──
        header = ctk.CTkFrame(modal, fg_color=("#F1F5F9", "#0F172A"), height=40)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="Select Products",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=(15, 0))

        ctk.CTkButton(
            header, text="×", width=30, height=26,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent", hover_color=("#E2E8F0", "#334155"),
            text_color=("#475569", "#CBD5E1"),
            command=modal.destroy
        ).pack(side="right", padx=(0, 8))

        # ── Search + Barcode row ──
        search_row = ctk.CTkFrame(modal, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=(10, 6))

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_row, textvariable=search_var,
            placeholder_text="Search by name, SKU, or barcode...",
            height=32
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        barcode_var = ctk.StringVar()
        barcode_entry = ctk.CTkEntry(
            search_row, textvariable=barcode_var,
            placeholder_text="Scan barcode...",
            width=140, height=32
        )
        barcode_entry.pack(side="left", padx=(0, 0))

        # ── Product tree ──
        tree_frame = ctk.CTkFrame(modal)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=6)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("SKU", "Name", "Stock", "Normal Price", "Workshop Price")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")

        tree.tag_configure("stock_zero", background="#7F1D1D", foreground="#FFFFFF",
                           font=("Segoe UI", 11, "bold"))
        tree.tag_configure("stock_low", background="#7F1D1D", foreground="#FFFFFF",
                           font=("Segoe UI", 11, "bold"))
        tree.tag_configure("stock_ok", background="#1E293B", foreground="#F8FAFC",
                           font=("Segoe UI", 11))

        col_widths = {"SKU": 90, "Name": 350, "Stock": 100, "Normal Price": 110, "Workshop Price": 110}
        for col in cols:
            anchor = "w" if col == "Name" else "center"
            tree.heading(col, text=col, anchor=anchor)
            tree.column(col, width=col_widths[col], anchor=anchor, minwidth=60)

        v_sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_sb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)
        v_sb.grid(row=0, column=1, sticky="ns")
        h_sb.grid(row=1, column=0, sticky="ew")

        # ── Footer ──
        footer = ctk.CTkFrame(modal, fg_color=("#F8FAFC", "#1E293B"), height=42)
        footer.pack(fill="x", padx=0, pady=0)
        footer.pack_propagate(False)

        count_label = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(size=11))
        count_label.pack(side="left", padx=(12, 0))

        add_btn = ctk.CTkButton(
            footer, text="🛒  Add to Cart",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32, width=140,
            fg_color="#4CAF50", hover_color="#45A049",
            state="disabled"
        )
        add_btn.pack(side="right", padx=(0, 12))

        # ── Populate helpers ──
        _current_filtered = []

        def _populate(product_list):
            nonlocal _current_filtered
            _current_filtered = list(product_list)
            for item in tree.get_children():
                tree.delete(item)
            for idx, p in enumerate(product_list):
                avail = self.get_available_stock(p)
                reorder = p['reorder_level']
                if avail <= 0:
                    tag = "stock_zero"
                    disp = f"{avail}  Out of Stock"
                elif avail <= reorder:
                    tag = "stock_low"
                    disp = f"{avail}  Low"
                else:
                    tag = "stock_ok"
                    disp = f"{avail}"
                tree.insert("", "end", values=(
                    p['sku'], p['name'], disp,
                    _fmt(p['price_normal']), _fmt(p['price_workshop'])
                ), tags=(tag,))
            count_label.configure(
                text=f"Showing {len(product_list)} of {len(self.all_products)} products"
            )

        def _do_filter(*_):
            term = search_var.get().lower()
            if not term:
                _populate(self.all_products)
            else:
                filtered = [
                    p for p in self.all_products
                    if term in p['name'].lower()
                    or term in p['sku'].lower()
                    or (p.get('barcode') and term in p['barcode'].lower())
                ]
                _populate(filtered)
                if not filtered:
                    count_label.configure(text="No products found")

        def _add_selected():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if 0 <= idx < len(_current_filtered):
                product = _current_filtered[idx]
                self.add_to_cart(quantity=1, product=product)
                # flash‑feedback on the add button
                add_btn.configure(text="✅  Added!", fg_color="#10B981")
                modal.after(800, lambda: add_btn.configure(
                    text="🛒  Add to Cart", fg_color="#4CAF50"
                ))

        def _on_select(_=None):
            sel = tree.selection()
            add_btn.configure(state="normal" if sel else "disabled")

        def _on_double_click(_=None):
            _add_selected()

        # ── Barcode handler ──
        def _on_modal_barcode(_=None):
            code = barcode_var.get().strip()
            if not code:
                return
            barcode_var.set("")
            product = None
            for p in self.all_products:
                if p.get('barcode') and p['barcode'] == code:
                    product = p
                    break
            if not product:
                results = db.execute_query(
                    "SELECT product_id, sku, name, stock, price_normal, price_workshop, reorder_level, barcode "
                    "FROM products WHERE barcode = ? AND is_active = 1",
                    (code,)
                )
                if results:
                    product = results[0]
            if product:
                self.add_to_cart(quantity=1, product=product)
                add_btn.configure(text="✅  Added!", fg_color="#10B981")
                modal.after(800, lambda: add_btn.configure(
                    text="🛒  Add to Cart", fg_color="#4CAF50"
                ))
                # Highlight in tree
                for item_id in tree.get_children():
                    vals = tree.item(item_id, 'values')
                    if vals and vals[0] == product['sku']:
                        tree.selection_set(item_id)
                        tree.focus(item_id)
                        tree.see(item_id)
                        _on_select()
                        break
                return
            # Not found — flash red on entry
            barcode_entry.configure(border_color="#ef4444")
            modal.after(1500, lambda: barcode_entry.configure(
                border_color=("#565b5e", "#949A9F")
            ))

        # ── Bindings ──
        search_var.trace('w', _do_filter)
        barcode_entry.bind("<Return>", _on_modal_barcode)
        tree.bind("<<TreeviewSelect>>", _on_select)
        tree.bind("<Double-1>", _on_double_click)
        add_btn.configure(command=_add_selected)
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)

        # ── Initial population ──
        if initial_search:
            search_var.set(initial_search)
            _do_filter()
        else:
            _populate(self.all_products)
        search_entry.focus_set()

    def create_cart_section(self, parent):
        """(Deprecated) Kept for backward compat — cart is now built inside product_frame."""
        self._build_cart_in_product(parent)

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
        """Load products into memory for the modal browser."""
        try:
            query = """
                SELECT p.product_id, p.sku, p.name, p.stock, p.price_normal, 
                       p.price_workshop, p.reorder_level, p.barcode
                FROM products p
                WHERE p.is_active = 1
                ORDER BY p.name
            """
            self.all_products = db.execute_query(query)
        except Exception as e:
            print(f"Error loading products: {e}")
            self.all_products = []
    
    def refresh_table_tags(self):
        """Re-apply stock status tag colors."""
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

    def on_customer_selected(self, customer_name):
        """Handle customer selection"""
        self.current_customer = self.customers_data.get(customer_name)
        self.update_cart_display()
        self._update_customer_info()

    def _update_customer_info(self):
        """Update customer info display below dropdown"""
        if not hasattr(self, 'customer_info_frame'):
            return
        customer = self.current_customer
        if not customer or customer.get('customer_id') is None:
            data = db.execute_query(
                "SELECT name, contact, credit_balance FROM customers WHERE name = 'Walk-in Customer'"
            )
            if data:
                c = data[0]
                self.customer_name_val.configure(text=c['name'])
                self.customer_phone_val.configure(text=c.get('contact', 'N/A') or 'N/A')
                self.customer_credit_val.configure(text=f"Rs {c.get('credit_balance', 0):,.2f}")
                return
            self.customer_name_val.configure(text="Walk-in Customer")
            self.customer_phone_val.configure(text="N/A")
            self.customer_credit_val.configure(text="Rs 0.00")
        else:
            data = db.execute_query(
                "SELECT name, contact, credit_balance FROM customers WHERE customer_id = ?",
                (customer['customer_id'],)
            )
            if data:
                c = data[0]
                self.customer_name_val.configure(text=c['name'])
                self.customer_phone_val.configure(text=c.get('contact', 'N/A') or 'N/A')
                self.customer_credit_val.configure(text=f"Rs {c.get('credit_balance', 0):,.2f}")

    def _on_barcode_scanned(self, event=None):
        """Barcode scanned — find product and add directly to cart."""
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
            results = db.execute_query(
                "SELECT product_id, sku, name, stock, price_normal, price_workshop, reorder_level, barcode "
                "FROM products WHERE barcode = ? AND is_active = 1",
                (code,)
            )
            if results:
                product = results[0]
        if not product:
            self.barcode_entry.configure(border_color="#ef4444")
            self.barcode_status.configure(text="❌ Not found", text_color="#ef4444")
            self.parent.after(2000, lambda: (
                self.barcode_entry.configure(border_color=("#565b5e", "#949A9F")),
                self.barcode_status.configure(text="")
            ))
            self.barcode_entry.focus_set()
            return
        available = self.get_available_stock(product)
        if available <= 0:
            self.barcode_entry.configure(border_color="#ef4444")
            self.barcode_status.configure(text=f"❌ Out of stock: {product['name'][:15]}", text_color="#ef4444")
            self.parent.after(2000, lambda: (
                self.barcode_entry.configure(border_color=("#565b5e", "#949A9F")),
                self.barcode_status.configure(text="")
            ))
            self.barcode_entry.focus_set()
            return
        self.add_to_cart(quantity=1, product=product)
        self.barcode_entry.configure(border_color="#10b981")
        self.barcode_status.configure(text="✅ Added to cart", text_color="#10b981")
        self.parent.after(1000, lambda: (
            self.barcode_entry.configure(border_color=("#565b5e", "#949A9F")),
            self.barcode_status.configure(text="")
        ))
        self.barcode_entry.focus_set()

    def add_to_cart(self, quantity=1, product=None):
        """Add a product to cart. Pass a product dict directly, or it will show the browse prompt."""
        if product is None:
            messagebox.showinfo("Browse Products", "Please use the 'Browse Products' button to search and select products.")
            return
        
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
            new_quantity = existing_item['quantity'] + quantity
            if new_quantity > product['stock']:
                avail = product['stock'] - existing_item['quantity']
                if avail > 0:
                    messagebox.showwarning("Warning", f"Only {avail} more units can be added.")
                    existing_item['quantity'] = product['stock']
                else:
                    messagebox.showwarning("Warning", "Maximum quantity already in cart.")
                    return
            else:
                existing_item['quantity'] = new_quantity
        else:
            self.cart_items.append({
                'product_id': product['product_id'],
                'sku': product['sku'],
                'name': product['name'],
                'quantity': quantity,
                'price_normal': product['price_normal'],
                'price_workshop': product['price_workshop'],
                'stock': product['stock']
            })
        
        self.update_cart_display()
    
    def _remove_cart_item(self, idx):
        """Remove a cart item by index (inline button handler)."""
        if 0 <= idx < len(self.cart_items):
            self.cart_items.pop(idx)
            self.update_cart_display()

    def _dec_cart_item(self, idx):
        """Decrease quantity of cart item by 1 (inline button handler)."""
        if 0 <= idx < len(self.cart_items):
            if self.cart_items[idx]['quantity'] > 1:
                self.cart_items[idx]['quantity'] -= 1
            else:
                self.cart_items.pop(idx)
            self.update_cart_display()

    def _inc_cart_item(self, idx):
        """Increase quantity of cart item by 1 (inline button handler)."""
        if 0 <= idx < len(self.cart_items):
            item = self.cart_items[idx]
            product = None
            for p in self.all_products:
                if p['product_id'] == item['product_id']:
                    product = p
                    break
            if product:
                available = self.get_available_stock(product)
                if available <= 0:
                    return
                self.cart_items[idx]['quantity'] += 1
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            if messagebox.askyesno("Confirm", "Clear all items from cart?"):
                self.cart_items = []
                self.update_cart_display()

    def update_cart_display(self):
        """Update cart display with inline controls and totals"""
        # Destroy item rows but keep cart_empty_label
        for w in self.cart_items_container.winfo_children():
            if w != self.cart_empty_label:
                w.destroy()

        subtotal = 0
        customer_type = self.current_customer['type'] if self.current_customer else 'Normal'

        if not self.cart_items:
            self.cart_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.cart_empty_label.place_forget()

        # Build each cart item as a row with inline controls
        for idx, item in enumerate(self.cart_items):
            if customer_type == 'Workshop':
                unit_price = item['price_workshop']
            else:
                unit_price = item['price_normal']
            
            total_price = unit_price * item['quantity']
            subtotal += total_price

            bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
            is_dark = ctk.get_appearance_mode() == "Dark"
            if is_dark:
                bg = "#1E1E2E" if idx % 2 == 0 else "#1A1A2E"

            row_frame = ctk.CTkFrame(self.cart_items_container, fg_color=bg, height=34)
            row_frame.pack(fill="x", padx=1, pady=(0, 1))
            row_frame.pack_propagate(False)

            # Product name — also retrieve stock for tooltip
            product_name = item['name']
            stock_info = 0
            for p in self.all_products:
                if p['product_id'] == item['product_id']:
                    stock_info = self.get_available_stock(p)
                    break
            tooltip_text = f"{product_name} — Stock: {stock_info}"

            name_label = ctk.CTkLabel(row_frame, text=product_name[:18] + ".." if len(product_name) > 18 else product_name,
                                      font=ctk.CTkFont(size=10), anchor="w")
            name_label.pack(side="left", padx=(8, 0), expand=True, fill="x")

            # Tooltip on row frame
            row_frame.bind("<Enter>", lambda e, t=tooltip_text: self._show_tooltip(e, t))
            row_frame.bind("<Leave>", lambda e: self._hide_tooltip())
            name_label.bind("<Enter>", lambda e, t=tooltip_text: self._show_tooltip(e, t))
            name_label.bind("<Leave>", lambda e: self._hide_tooltip())

            # [-] button
            dec_btn = ctk.CTkButton(
                row_frame, text="−", width=26, height=24,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("#FF6B35", "#D35400"), hover_color=("#E55A2B", "#B64900"),
                command=lambda i=idx: self._dec_cart_item(i)
            )
            dec_btn.pack(side="left", padx=(2, 1))
            if item['quantity'] <= 1:
                dec_btn.configure(state="disabled")

            # Qty label
            qty_lbl = ctk.CTkLabel(row_frame, text=str(item['quantity']),
                                    font=ctk.CTkFont(size=11, weight="bold"), width=22)
            qty_lbl.pack(side="left", padx=(1, 1))

            # [+] button
            inc_btn = ctk.CTkButton(
                row_frame, text="+", width=26, height=24,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("#2196F3", "#1565C0"), hover_color=("#1976D2", "#0D47A1"),
                command=lambda i=idx: self._inc_cart_item(i)
            )
            inc_btn.pack(side="left", padx=(1, 4))

            # Check stock for inc button
            product = None
            for p in self.all_products:
                if p['product_id'] == item['product_id']:
                    product = p
                    break
            if product:
                available = self.get_available_stock(product)
                if available <= 0:
                    inc_btn.configure(state="disabled")
            
            # Price label
            ctk.CTkLabel(row_frame, text=_fmt(unit_price),
                         font=ctk.CTkFont(size=10),
                         text_color=("#64748B", "#94A3B8")).pack(side="right", padx=(0, 4))

            # Total label
            ctk.CTkLabel(row_frame, text=_fmt(total_price),
                         font=ctk.CTkFont(size=10, weight="bold")).pack(side="right", padx=(0, 4))

            # [×] remove button
            remove_btn = ctk.CTkButton(
                row_frame, text="×", width=24, height=22,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("#FEE2E2", "#3B0A0A"), hover_color=("#FECACA", "#5B1A1A"),
                text_color=("#DC2626", "#FCA5A5"),
                command=lambda i=idx: self._remove_cart_item(i)
            )
            remove_btn.pack(side="right", padx=(2, 4))

        # Calculate discount and final total
        discount_amount = 0
        if self.discount_amount > 0 or self.discount_percentage > 0:
            if self.discount_type == "amount":
                discount_amount = min(self.discount_amount, subtotal)
            else:
                discount_amount = (subtotal * self.discount_percentage) / 100
        
        final_total = subtotal - discount_amount

        # Update summary labels
        self.subtotal_value.configure(text=_fmt(subtotal))

        if discount_amount > 0:
            if self.discount_type == "amount":
                self.discount_value.configure(text=f"-Rs{discount_amount:.2f}")
            else:
                self.discount_value.configure(text=f"-Rs{discount_amount:.2f} ({self.discount_percentage:.1f}%)")
        else:
            self.discount_value.configure(text="")

        self.total_value.configure(text=f"Rs {final_total:,.2f}")

        # Update cart badge
        count = len(self.cart_items)
        self.cart_badge.configure(text=f"({count})")

        # Update proceed button
        has_items = count > 0
        if has_items:
            self.proceed_btn.configure(
                text=f"Proceed Sale - Rs {final_total:,.2f}",
                state="normal",
                fg_color="#10B981",
                text_color="#FFFFFF",
                hover_color="#059669"
            )
        else:
            self.proceed_btn.configure(
                text="Proceed Sale - Rs 0.00",
                state="disabled",
                fg_color="#374151",
                text_color="#9CA3AF",
                hover_color="#374151"
            )

    
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

        # Outstanding credit sales table (fixed 250px height)
        table_frame = ctk.CTkFrame(scroll, height=250)
        table_frame.pack(fill="x", padx=10, pady=0)
        table_frame.pack_propagate(False)

        table_container = ctk.CTkFrame(table_frame)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        columns = ("Invoice", "Date", "Customer", "Total", "Paid", "Outstanding")
        self.credit_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=5)
        table_styles.apply_credit_sales_style(self.credit_tree)

        col_widths = {"Invoice": 160, "Date": 110, "Customer": 220,
                      "Total": 120, "Paid": 120, "Outstanding": 130}
        for col in columns:
            self.credit_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.credit_tree.column(col, width=col_widths.get(col, 120), anchor="center", minwidth=80)

        v_sb = ttk.Scrollbar(table_container, orient="vertical", command=self.credit_tree.yview)
        h_sb = ttk.Scrollbar(table_container, orient="horizontal", command=self.credit_tree.xview)
        self.credit_tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)

        self.credit_tree.grid(row=0, column=0, sticky="nsew")
        v_sb.grid(row=0, column=1, sticky="ns")
        h_sb.grid(row=1, column=0, sticky="ew")

        # Compact empty-state for credit tree
        self.credit_empty_label = ctk.CTkLabel(
            table_container,
            text="No outstanding credit sales",
            font=ctk.CTkFont(size=12),
            text_color=("#94A3B8", "#64748B")
        )

        # Action buttons
        actions_frame = ctk.CTkFrame(scroll)
        actions_frame.pack(fill="x", padx=10, pady=10)

        self.credit_pay_btn = ctk.CTkButton(
            actions_frame,
            text="💰 Record Payment",
            command=self.pay_credit_from_tab,
            width=150, height=38,
            state="disabled",
            fg_color="#059669", hover_color="#047857",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.credit_pay_btn.pack(side="left", padx=5)
        self.credit_tree.bind("<<TreeviewSelect>>", self._on_credit_select)

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

        history_table_frame = ctk.CTkFrame(scroll, height=200)
        history_table_frame.pack(fill="x", padx=10, pady=(0, 10))
        history_table_frame.pack_propagate(False)

        history_container = ctk.CTkFrame(history_table_frame)
        history_container.pack(fill="both", expand=True, padx=5, pady=5)
        history_container.grid_columnconfigure(0, weight=1)
        history_container.grid_rowconfigure(0, weight=1)

        hist_cols = ("Date", "Invoice", "Customer", "Amount Paid", "Remaining After", "Recorded At")
        self.payment_history_tree = ttk.Treeview(history_container, columns=hist_cols, show="headings", height=5)
        table_styles.apply_credit_payment_style(self.payment_history_tree)

        hist_widths = {"Date": 100, "Invoice": 160, "Customer": 180,
                       "Amount Paid": 120, "Remaining After": 130, "Recorded At": 150}
        for col in hist_cols:
            self.payment_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.payment_history_tree.column(col, width=hist_widths.get(col, 120), anchor="center", minwidth=80)

        ph_vsb = ttk.Scrollbar(history_container, orient="vertical", command=self.payment_history_tree.yview)
        ph_hsb = ttk.Scrollbar(history_container, orient="horizontal", command=self.payment_history_tree.xview)
        self.payment_history_tree.configure(yscrollcommand=ph_vsb.set, xscrollcommand=ph_hsb.set)

        self.payment_history_tree.grid(row=0, column=0, sticky="nsew")
        ph_vsb.grid(row=0, column=1, sticky="ns")
        ph_hsb.grid(row=1, column=0, sticky="ew")

        # Compact empty-state for payment history
        self.payment_empty_label = ctk.CTkLabel(
            history_container,
            text="No credit payment history",
            font=ctk.CTkFont(size=12),
            text_color=("#94A3B8", "#64748B")
        )

    def _on_credit_select(self, event=None):
        """Enable/disable Record Payment button based on credit tree selection."""
        sel = self.credit_tree.selection()
        self.credit_pay_btn.configure(state="normal" if sel else "disabled")

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

            # Toggle empty state — overlay label when no data, treeview stays
            if count == 0:
                self.credit_empty_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.credit_empty_label.place_forget()

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

            # Toggle empty state
            if not records:
                self.payment_empty_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.payment_empty_label.place_forget()

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

        # Query DB directly for fresh data with status/balance verification
        sale = db.execute_query("""
            SELECT s.id, s.invoice_number, s.sale_date, s.total_amount, s.paid_amount,
                   (s.total_amount - s.paid_amount) as balance, s.status, s.customer_id,
                   COALESCE(c.name, 'Walk-in Customer') as customer_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.invoice_number = ?
        """, (invoice_number,))

        if not sale:
            messagebox.showerror("Error", "Sale not found.")
            return

        sale = sale[0]

        if sale['status'] != 'credit':
            messagebox.showinfo(
                "Not a Credit Sale",
                f"Invoice {invoice_number} is not a credit sale."
            )
            return

        if sale['balance'] <= 0.01:
            messagebox.showinfo(
                "No Balance",
                f"Invoice {invoice_number} is already fully paid."
            )
            return

        dialog = PaySaleCreditDialog(self.parent, sale)
        if dialog.result:
            self.load_sales_history()

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
    
    def _quick_discount_percentage(self, pct_str):
        """Apply a quick percentage discount button"""
        pct = float(pct_str.replace("%", ""))
        if not self.cart_items:
            return
        self.discount_type_var.set("percentage")
        self.discount_type = "percentage"
        self.discount_percentage = pct
        self.discount_amount = 0
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, str(pct))
        self.update_cart_display()

    def _on_proceed_sale(self):
        """Handle proceed sale button click with visual feedback"""
        if not self.cart_items:
            return
        self.proceed_btn.configure(text="Processing...", state="disabled")
        self.parent.after(50, self._do_process_sale)

    def _do_process_sale(self):
        """Execute the sale processing and revert button on completion"""
        try:
            self.process_sale()
        finally:
            self.proceed_btn.configure(state="normal")
            self.update_cart_display()

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
    def __init__(self, parent, sale_data, refresh_callback=None):
        self.parent = parent
        self.sale_data = sale_data
        self.refresh_callback = refresh_callback
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

        # Parse previous returns from notes
        self._returned_data = self._parse_returns()
        self._has_returns = bool(self._returned_data)

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
        status_text = self.sale_data['status'].title()
        info_text = f"""
        Date: {self.sale_data['sale_date']}
        Customer: {self.sale_data['customer_name'] or 'Walk-in Customer'}
        Payment Method: {self.sale_data['payment_method'].title()}
        Status: {status_text}{'  |  ↩ Returns: Yes' if self._has_returns else ''}
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
        remaining = self.load_sale_items(items_frame)

        # If there were returns, show return history
        if self._has_returns:
            ret_label = ctk.CTkLabel(
                main_frame,
                text="📋 Return History:",
                font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
            )
            ret_label.pack(fill="x", pady=(10, 5))

            ret_frame = ctk.CTkFrame(main_frame)
            ret_frame.pack(fill="x")

            self._load_return_history(ret_frame)

        # Action buttons
        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(15, 0))

        can_return = remaining > 0
        return_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Process Return",
            command=self._open_return,
            width=150,
            height=38,
            fg_color="#f59e0b" if can_return else "#9CA3AF",
            hover_color="#d97706" if can_return else "#9CA3AF",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="normal" if can_return else "disabled"
        )
        return_btn.pack(side="left")

        # Close button
        close_btn = ctk.CTkButton(
            actions_frame,
            text="Close",
            command=self.dialog.destroy,
            width=100,
            height=38
        )
        close_btn.pack(side="right")

    def _open_return(self):
        """Open the sales return dialog."""
        dialog = SaleReturnDialog(self.dialog, self.sale_data, self.refresh_callback)
        if dialog.returns_processed:
            self.dialog.destroy()
    
    def _parse_returns(self):
        """Parse return data from sale notes. Returns dict of product_id -> total_returned_qty."""
        returned = {}
        notes = self.sale_data.get('notes') or ""
        for line in notes.split('\n'):
            line = line.strip()
            if line.startswith('[Return]') and 'items=' in line:
                try:
                    items_part = line.split('items=')[1].split(' refund=')[0]
                    import json
                    items_data = json.loads(items_part.replace("'", '"'))
                    for pid, qty in items_data.items():
                        returned[pid] = returned.get(pid, 0) + qty
                except Exception:
                    pass
        return returned

    def _get_return_history(self):
        """Get human-readable return history lines from notes."""
        entries = []
        notes = self.sale_data.get('notes') or ""
        for line in notes.split('\n'):
            line = line.strip()
            if line.startswith('[Return]'):
                entries.append(line)
        return entries

    def _load_return_history(self, parent):
        """Show a simple list of return history entries."""
        entries = self._get_return_history()
        if not entries:
            ctk.CTkLabel(
                parent, text="No returns recorded.",
                font=ctk.CTkFont(size=11), text_color=("#94A3B8", "#64748B")
            ).pack(pady=5)
            return
        for entry in entries:
            ctk.CTkLabel(
                parent, text=entry,
                font=ctk.CTkFont(size=11), anchor="w", justify="left",
                text_color=("#b91c1c", "#fca5a5")
            ).pack(fill="x", padx=5, pady=1)

    def load_sale_items(self, parent):
        """Load and display sale items, showing returned quantities where applicable."""
        try:
            query = """
                SELECT si.id, si.product_id, si.quantity, si.unit_price, si.total, p.name, p.sku
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """
            items = db.execute_query(query, (self.sale_data['sale_id'],))
            
            # Create treeview for items with enhanced styling
            columns = ("SKU", "Product", "Sold", "Returned", "Remaining", "Unit Price", "Total")
            items_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
            
            # Apply centralized styling
            table_styles.apply_sale_details_style(items_tree)
            
            # Define headings and column widths
            column_widths = {"SKU": 100, "Product": 180, "Sold": 55, "Returned": 70,
                           "Remaining": 70, "Unit Price": 100, "Total": 100}
            
            for col in columns:
                items_tree.heading(col, text=f"  {col}  ", anchor="center")
                items_tree.column(col, width=column_widths.get(col, 100),
                                  anchor="center" if col != "Product" else "w", minwidth=50)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=items_tree.yview)
            items_tree.configure(yscrollcommand=v_scrollbar.set)
            
            # Pack table and scrollbar
            items_tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            
            remaining_total = 0
            for item in items:
                pid = item['product_id']
                returned_qty = self._returned_data.get(str(pid), 0)
                sold = item['quantity']
                remaining = max(sold - returned_qty, 0)
                remaining_total += remaining
                
                returned_str = str(returned_qty) if returned_qty > 0 else "-"
                
                tag = 'returned' if returned_qty > 0 else ''
                items_tree.insert("", "end", values=(
                    item['sku'],
                    item['name'],
                    sold,
                    returned_str,
                    remaining,
                    _fmt(item['unit_price']),
                    _fmt(item['total'])
                ), tags=(tag,) if tag else ())
            
            if items_tree.tag_has('returned'):
                items_tree.tag_configure('returned', foreground='#dc2626')
            
            return remaining_total
                
        except Exception as e:
            print(f"Error loading sale items: {e}")
            error_label = ctk.CTkLabel(
                parent,
                text="Error loading sale items",
                font=ctk.CTkFont(size=12)
            )
            error_label.pack(pady=20)
            return 0


class SaleReturnDialog:
    """Dialog to process return of items from a completed sale."""

    def __init__(self, parent, sale_data, refresh_callback=None):
        self.parent = parent
        self.sale_data = sale_data
        self.refresh_callback = refresh_callback
        self.returns_processed = False
        self._items = []
        self._qty_vars = {}
        self._price_vars = {}
        self._price_entries = {}

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Sales Return - {sale_data['invoice_number']}")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._load_items()
        self._build_ui()

        center_window_on_screen(self.dialog, 700, 540)
        self.dialog.wait_window()

    def _parse_previous_returns(self):
        """Parse notes to get already-returned quantities per product_id."""
        returned = {}
        notes = self.sale_data.get('notes') or ""
        for line in notes.split('\n'):
            line = line.strip()
            if line.startswith('[Return]') and 'items=' in line:
                try:
                    items_part = line.split('items=')[1].split(' refund=')[0]
                    # Format: {product_id:qty,product_id:qty,...}
                    import json
                    returned.update(json.loads(items_part.replace("'", '"')))
                except Exception:
                    pass
        return returned

    def _calc_discount_factor(self):
        """Calculate proportional discount factor."""
        subtotal = self.sale_data.get('subtotal') or 0
        total = self.sale_data.get('total_amount') or 0
        if subtotal and subtotal > 0 and total < subtotal:
            return total / subtotal
        return 1.0

    def _load_items(self):
        try:
            items = db.execute_query("""
                SELECT si.id, si.product_id, si.quantity, si.unit_price, si.total,
                       p.name, p.sku, p.stock
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.name
            """, (self.sale_data['sale_id'],))
        except Exception as e:
            print(f"Error loading sale items: {e}")
            items = []

        already_returned = self._parse_previous_returns()
        discount_factor = self._calc_discount_factor()

        self._items = []
        for item in items:
            pid = item['product_id']
            prev = already_returned.get(str(pid), 0)
            avail = item['quantity'] - prev
            default_price = item['unit_price'] * discount_factor
            self._items.append({
                **item,
                'already_returned': prev,
                'available': max(avail, 0),
                'default_refund_price': default_price,
            })

    def _build_ui(self):
        main = ctk.CTkScrollableFrame(self.dialog)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(main, corner_radius=10, fg_color=("#fef3c7", "#92400e"))
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header, text="🔄 Sales Return",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(12, 2))

        discount_info = ""
        if self._calc_discount_factor() < 1.0:
            discount_info = f" (discount applied: {1 - self._calc_discount_factor():.0%})"

        ctk.CTkLabel(
            header,
            text=f"{self.sale_data['invoice_number']} — {self.sale_data.get('customer_name', 'Walk-in Customer')}{discount_info}",
            font=ctk.CTkFont(size=12),
            text_color=("#78350f", "#fef3c7")
        ).pack(pady=(0, 12))

        # Items list
        ctk.CTkLabel(
            main, text="Select items to return:",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(0, 8))

        items_container = ctk.CTkFrame(main)
        items_container.pack(fill="both", expand=True)

        # Column headers
        header_row = ctk.CTkFrame(items_container, fg_color=("#F1F5F9", "#0F172A"), height=30)
        header_row.pack(fill="x")
        header_row.pack_propagate(False)

        hd = [("Product", 0, 2, "w"), ("SKU", 2, 1, "center"), ("Sold", 3, 1, "center"),
              ("Avail", 4, 1, "center"), ("Return Qty", 5, 1, "center"), ("Refund Price", 6, 1, "center")]
        for text, col, weight, anc in hd:
            header_row.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(
                header_row, text=text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=("#475569", "#94A3B8")
            ).grid(row=0, column=col, columnspan=weight, sticky="ew", padx=4)

        # Scrollable items
        items_scroll = ctk.CTkScrollableFrame(items_container, height=200)
        items_scroll.pack(fill="both", expand=True, pady=(2, 0))

        for idx, item in enumerate(self._items):
            bg = ("#FFFFFF", "#1E1E2E") if idx % 2 == 0 else ("#F8FAFC", "#262636")
            row_f = ctk.CTkFrame(items_scroll, fg_color=bg, height=36)
            row_f.pack(fill="x")
            row_f.pack_propagate(False)

            row_f.grid_columnconfigure(0, weight=2)
            row_f.grid_columnconfigure(1, weight=1)
            row_f.grid_columnconfigure(2, weight=1)
            row_f.grid_columnconfigure(3, weight=1)
            row_f.grid_columnconfigure(4, weight=1)
            row_f.grid_columnconfigure(5, weight=1)

            ctk.CTkLabel(row_f, text=item['name'], font=ctk.CTkFont(size=11), anchor="w").grid(row=0, column=0, sticky="w", padx=(10, 4))
            ctk.CTkLabel(row_f, text=item['sku'], font=ctk.CTkFont(size=10), text_color=("#64748B", "#94A3B8")).grid(row=0, column=1, sticky="ew")

            sold_str = str(item['quantity'])
            if item['already_returned'] > 0:
                sold_str = f"{item['quantity']} (-{item['already_returned']})"
            ctk.CTkLabel(row_f, text=sold_str, font=ctk.CTkFont(size=11)).grid(row=0, column=2, sticky="ew")
            ctk.CTkLabel(row_f, text=str(item['available']), font=ctk.CTkFont(size=11)).grid(row=0, column=3, sticky="ew")

            # Return Qty entry
            qvar = tk.StringVar(value="0")
            qvar.trace('w', lambda *a: self._on_change())
            self._qty_vars[item['id']] = qvar
            qty_e = ctk.CTkEntry(
                row_f, textvariable=qvar,
                font=ctk.CTkFont(size=12), justify="center",
                height=28, width=60, corner_radius=4
            )
            qty_e.grid(row=0, column=4, sticky="ew", padx=(4, 4))

            # Refund Price entry
            pvar = tk.StringVar(value=f"{item['default_refund_price']:.2f}")
            pvar.trace('w', lambda *a: self._on_change())
            self._price_vars[item['id']] = pvar
            price_e = ctk.CTkEntry(
                row_f, textvariable=pvar,
                font=ctk.CTkFont(size=12), justify="center",
                height=28, width=80, corner_radius=4
            )
            price_e.grid(row=0, column=5, sticky="ew", padx=(4, 10))
            self._price_entries[item['id']] = price_e

        # Total refund
        total_frame = ctk.CTkFrame(main, fg_color="transparent")
        total_frame.pack(fill="x", pady=(10, 5))

        self.total_refund_label = ctk.CTkLabel(
            total_frame, text="Total Refund: Rs0.00",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f59e0b"
        )
        self.total_refund_label.pack(side="left", padx=5)

        # Buttons
        actions = ctk.CTkFrame(main, fg_color="transparent")
        actions.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            actions, text="❌ Cancel",
            command=self.dialog.destroy,
            width=100, height=40, corner_radius=10,
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#e53935", "#c62828"),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right", padx=(5, 0))

        self.confirm_btn = ctk.CTkButton(
            actions, text="✅ Confirm Return",
            command=self._confirm_return,
            width=160, height=40, corner_radius=10,
            fg_color="#059669", hover_color="#047857",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled"
        )
        self.confirm_btn.pack(side="right")

    def _get_qty(self, item):
        var = self._qty_vars.get(item['id'])
        if not var:
            return 0
        try:
            qty = int(var.get())
        except (ValueError, TypeError):
            return 0
        return max(0, min(qty, item['available']))

    def _get_price(self, item):
        var = self._price_vars.get(item['id'])
        if not var:
            return 0.0
        try:
            return float(var.get())
        except (ValueError, TypeError):
            return 0.0

    def _on_change(self):
        total_refund = 0.0
        has_returns = False
        has_invalid_price = False
        for item in self._items:
            qty = self._get_qty(item)
            price = self._get_price(item)
            entry = self._price_entries.get(item['id'])
            if qty > 0:
                has_returns = True
                if price <= 0:
                    has_invalid_price = True
                    if entry:
                        entry.configure(border_color="#ef4444")
                else:
                    if entry:
                        entry.configure(border_color=("#CBD5E1", "#334155"))
                total_refund += qty * price
            else:
                if entry:
                    entry.configure(border_color=("#CBD5E1", "#334155"))

        self.total_refund_label.configure(text=f"Total Refund: {_fmt(total_refund)}")
        self.confirm_btn.configure(
            state="normal" if has_returns and not has_invalid_price else "disabled"
        )

    def _confirm_return(self):
        returns = []
        for item in self._items:
            qty = self._get_qty(item)
            if qty > 0:
                returns.append((item, qty))

        if not returns:
            messagebox.showwarning("Warning", "No items selected for return.")
            return

        # Validate refund prices
        zero_price_items = [(i, q) for i, q in returns if self._get_price(i) <= 0]
        if zero_price_items:
            names = ", ".join(i['name'] for i, _ in zero_price_items)
            messagebox.showerror(
                "Invalid Refund Price",
                f"Refund price must be greater than 0 for:\n{names}"
            )
            return

        total_refund = sum(qty * self._get_price(item) for item, qty in returns)

        confirm_msg = f"Process return of {len(returns)} item(s)?\n"
        for item, qty in returns:
            price = self._get_price(item)
            confirm_msg += f"  • {item['name']} × {qty} @ {_fmt(price)} = {_fmt(qty * price)}\n"
        confirm_msg += f"\nTotal refund amount: {_fmt(total_refund)}\n"
        confirm_msg += "\nStock will be adjusted accordingly."

        if not messagebox.askyesno("Confirm Return", confirm_msg):
            return

        try:
            for item, qty in returns:
                db.execute_update("""
                    UPDATE products SET stock = stock + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                """, (qty, item['product_id']))

            # Track per-item return quantities in notes for future returns
            items_returned = {str(item['product_id']): qty for item, qty in returns}
            existing_notes = self.sale_data.get('notes') or ""
            return_note = (
                f"[Return] {datetime.now().strftime('%Y-%m-%d %H:%M')}: "
                f"items={items_returned} refund={_fmt(total_refund)}"
            )
            new_notes = (existing_notes + "\n" + return_note) if existing_notes else return_note

            db.execute_update("""
                UPDATE sales SET notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_notes, self.sale_data['sale_id']))

            self.returns_processed = True
            if self.refresh_callback:
                self.refresh_callback()
            messagebox.showinfo(
                "Return Processed",
                f"Return processed successfully.\n{len(returns)} item(s) returned.\nRefund amount: {_fmt(total_refund)}"
            )
            self.dialog.destroy()

        except Exception as e:
            print(f"Error processing return: {e}")
            messagebox.showerror("Error", f"Failed to process return: {e}")


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
