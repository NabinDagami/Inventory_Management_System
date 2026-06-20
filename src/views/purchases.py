import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
import utils.simple_table_styles as table_styles

class PurchasesView:
    def __init__(self, parent):
        self.parent = parent
        self.purchase_items = []
        self.current_supplier = None
        self.all_products = []  # Initialize products list
        self.suppliers_data = {}  # Initialize suppliers data
        self.create_purchases_interface()
        self.load_suppliers()
        self.load_products()
    
    def create_purchases_interface(self):
        """Create the purchases management interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        tab_frame.pack(side="left", padx=10, pady=10)
        
        self.new_purchase_btn = ctk.CTkButton(
            tab_frame,
            text="🛒 New Purchase",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.switch_tab("new_purchase")
        )
        self.new_purchase_btn.pack(side="left", padx=(0, 15))
        
        self.purchase_history_btn = ctk.CTkButton(
            tab_frame,
            text="📋 Purchase History",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray10", "gray90"),
            command=lambda: self.switch_tab("purchase_history")
        )
        self.purchase_history_btn.pack(side="left")
        
        # Current tab tracking
        self.current_tab = "new_purchase"
        
        # Content container — holds both tabs; each tab manages its own scrolling
        self.content_container = ctk.CTkFrame(main_frame)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create both interfaces
        self.create_new_purchase_interface()
        self.create_purchase_history_interface()
        
        # Show new purchase interface by default
        self.switch_tab("new_purchase")
    
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
        inactive_text_color = ("gray40", "gray80")
        
        if tab_name == "new_purchase":
            self.new_purchase_btn.configure(fg_color=active_color, text_color="white")
            self.purchase_history_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
        else:
            self.new_purchase_btn.configure(fg_color=inactive_color, text_color=inactive_text_color)
            self.purchase_history_btn.configure(fg_color=active_color, text_color="white")
        
        # Show/hide appropriate interface
        if tab_name == "new_purchase":
            self.new_purchase_frame.pack(fill="both", expand=True)
            self.purchase_history_frame.pack_forget()
        else:
            self.new_purchase_frame.pack_forget()
            self.purchase_history_frame.pack(fill="both", expand=True)
            self.load_purchase_history()
    
    def create_new_purchase_interface(self):
        """Create the new purchase interface — scrollable body + fixed footer with totals."""
        self.new_purchase_frame = ctk.CTkFrame(self.content_container)

        # Supplier selection header
        header_frame = ctk.CTkFrame(self.new_purchase_frame)
        header_frame.pack(fill="x", padx=10, pady=10)

        supplier_label = ctk.CTkLabel(header_frame, text="Supplier:", font=ctk.CTkFont(size=14, weight="bold"))
        supplier_label.pack(side="left", padx=(10, 5), pady=10)

        self.supplier_var = tk.StringVar(value="Select Supplier...")
        self.supplier_dropdown = ctk.CTkOptionMenu(
            header_frame, 
            variable=self.supplier_var,
            command=self.on_supplier_selected,
            width=220
        )
        self.supplier_dropdown.pack(side="left", padx=5, pady=10)

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

        delivery_label = ctk.CTkLabel(header_frame, text="Expected Delivery:", font=ctk.CTkFont(size=14, weight="bold"))
        delivery_label.pack(side="left", padx=(20, 5), pady=10)

        self.delivery_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="YYYY-MM-DD",
            width=140
        )
        self.delivery_entry.pack(side="left", padx=5, pady=10)

        # ── Content area (compact, no outer scrollable — po_items_scroll handles item scrolling) ──
        content_frame = ctk.CTkFrame(self.new_purchase_frame)
        content_frame.pack(fill="x", padx=10, pady=(6, 0))
        content_frame.grid_columnconfigure(0, weight=1)

        # Product selection with embedded purchase order section
        self.create_product_selection(content_frame)

        # ── Footer (packs directly below content, no expand) ──────────────
        po_footer = ctk.CTkFrame(self.new_purchase_frame, fg_color=("#F0FDF4", "#0F172A"))
        po_footer.pack(fill="x", padx=10, pady=(0, 10))

        inner = ctk.CTkFrame(po_footer, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        def _summary_row(parent, label, color=None):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", pady=(0, 2))
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12)).pack(side="left")
            v = ctk.CTkLabel(r, text="Rs0.00", font=ctk.CTkFont(size=12, weight="bold"),
                              anchor="e", text_color=color or ("gray10", "gray90"))
            v.pack(side="right")
            return v

        self.subtotal_value = _summary_row(inner, "Subtotal")
        ctk.CTkFrame(inner, height=1, fg_color=("#CBD5E1", "#334155")).pack(fill="x", pady=4)

        total_row = ctk.CTkFrame(inner, fg_color="transparent")
        total_row.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(total_row, text="GRAND TOTAL", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.total_value = ctk.CTkLabel(total_row, text="Rs 0.00",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color="#10b981", anchor="e")
        self.total_value.pack(side="right")

        self.create_po_btn = ctk.CTkButton(
            po_footer, text="📋 Create Purchase Order",
            command=self.create_purchase_order,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            state="disabled",
            fg_color="#374151",
            text_color="#9CA3AF",
            hover_color="#374151"
        )
        self.create_po_btn.pack(fill="x", padx=12, pady=(0, 12))
    
    def create_purchase_history_interface(self):
        """Create the purchase history interface"""
        self.purchase_history_frame = ctk.CTkFrame(self.content_container)
        
        # Header with search and filters
        header_frame = ctk.CTkFrame(self.purchase_history_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_label = ctk.CTkLabel(header_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.purchase_search_var = tk.StringVar()
        self.purchase_search_var.trace('w', self.filter_purchase_history)
        search_entry = ctk.CTkEntry(
            header_frame,
            textvariable=self.purchase_search_var,
            placeholder_text="Search by PO number or supplier...",
            width=300
        )
        search_entry.pack(side="left", padx=5, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.load_purchase_history,
            width=100,
            height=35
        )
        refresh_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Purchase history table
        table_frame = ctk.CTkFrame(self.purchase_history_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for purchase history with enhanced styling
        columns = ("PO Number", "Date", "Supplier", "Items", "Total", "Status", "Expected Delivery")
        self.purchase_history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)
        
        # Apply centralized styling
        table_styles.apply_purchase_history_style(self.purchase_history_tree)
        
        # Define headings and column widths - bigger columns
        column_widths = {"PO Number": 150, "Date": 120, "Supplier": 180, "Items": 80, 
                        "Total": 120, "Status": 100, "Expected Delivery": 150}
        
        for col in columns:
            self.purchase_history_tree.heading(col, text=f"  {col}  ", anchor="center")
            self.purchase_history_tree.column(col, width=column_widths.get(col, 120), anchor="center", minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.purchase_history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.purchase_history_tree.xview)
        self.purchase_history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.purchase_history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(self.purchase_history_frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        view_details_btn = ctk.CTkButton(
            actions_frame,
            text="👁️ View Details",
            command=self.view_purchase_details,
            width=120,
            height=35
        )
        view_details_btn.pack(side="left", padx=5)
        
        receive_btn = ctk.CTkButton(
            actions_frame,
            text="📦 Mark as Received",
            command=self.mark_as_received,
            width=140,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        )
        receive_btn.pack(side="left", padx=5)
        
        # Double-click to view details
        self.purchase_history_tree.bind("<Double-1>", lambda e: self.view_purchase_details())
    
    def create_product_selection(self, parent):
        """Create product selection area with search, barcode, Browse button + modal (sales-style)."""
        product_frame = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"), corner_radius=6)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
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
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_keyrelease(e))
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
        self._build_purchase_order_in_product(product_frame)

    def _build_purchase_order_in_product(self, parent):
        """Build the purchase-order cart — grid-aligned header, empty-state, inline clear."""
        cart_outer = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#252535"),
                                   border_width=1, border_color=("#CBD5E1", "#334155"),
                                   corner_radius=6)
        cart_outer.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))

        # Header row: title + badge (left), Clear Cart (right)
        header_frame = ctk.CTkFrame(cart_outer, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(header_frame, text="📋 Purchase Order Items",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.po_badge = ctk.CTkLabel(
            header_frame, text="(0)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white", fg_color="#3b82f6",
            corner_radius=8, padx=8, pady=2
        )
        self.po_badge.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            header_frame, text="🗑 Clear Cart",
            command=self.clear_purchase_order, width=85, height=22,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=("#E2E8F0", "#334155"),
            text_color=("#475569", "#94A3B8"),
            hover_color=("#CBD5E1", "#475569")
        ).pack(side="right")

        # PO container (no scroll — main frame handles scrolling)
        self.po_container = ctk.CTkFrame(cart_outer, fg_color="transparent")
        self.po_container.pack(fill="x", padx=0, pady=0)

        # Column headers — uses same grid weights as item rows
        po_header_frame = ctk.CTkFrame(self.po_container, fg_color=("#F1F5F9", "#0F172A"), height=28)
        po_header_frame.pack(fill="x", padx=6, pady=(0, 2))
        po_header_frame.pack_propagate(False)
        po_header_frame.grid_columnconfigure(0, weight=4)
        po_header_frame.grid_columnconfigure(1, weight=1)
        po_header_frame.grid_columnconfigure(2, weight=1)
        po_header_frame.grid_columnconfigure(3, weight=1)
        po_header_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(po_header_frame, text="Product", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).grid(row=0, column=0, sticky="w", padx=(8, 4))
        ctk.CTkLabel(po_header_frame, text="Qty", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).grid(row=0, column=1)
        ctk.CTkLabel(po_header_frame, text="Total", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).grid(row=0, column=2, sticky="e")
        ctk.CTkLabel(po_header_frame, text="Unit Cost", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).grid(row=0, column=3, sticky="e")
        ctk.CTkLabel(po_header_frame, text="Remove", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=("#475569", "#94A3B8")).grid(row=0, column=4, sticky="e", padx=(0, 4))

        # ── Items container (fixed 200px, never expands — scrolls if many) ──
        self.po_items_scroll = ctk.CTkScrollableFrame(
            self.po_container, fg_color=("#FFFFFF", "#1E1E2E"), height=200
        )
        self.po_items_scroll.pack(fill="x", expand=False, padx=6, pady=2)

        # Centered empty-state label (shown/hidden via place)
        self.po_empty_label = ctk.CTkLabel(
            self.po_items_scroll,
            text="No items in purchase order. Search or browse products to add.",
            font=ctk.CTkFont(size=11),
            text_color=("#94A3B8", "#64748B"),
        )
        self.po_empty_label.place(relx=0.5, rely=0.5, anchor="center")

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
        w = max(self.search_entry.winfo_width(), 100)

        self._search_dropdown = ctk.CTkFrame(
            pf, fg_color="#1f2937", corner_radius=6,
            border_width=1, border_color="#4B5563"
        )
        self._search_dropdown.place(x=rel_x, y=rel_y, anchor="nw")

        inner = ctk.CTkScrollableFrame(self._search_dropdown, fg_color="#1f2937",
                                        scrollbar_button_hover_color="#4B5563",
                                        corner_radius=0)
        inner.pack(fill="both", expand=True)

        btn_w = w - 16

        for p in matches:
            name = p['name']
            full_label = name

            row = ctk.CTkFrame(inner, fg_color="transparent", height=32)
            row.pack(fill="x", padx=4, pady=(0, 1))
            row.pack_propagate(False)

            lbl = ctk.CTkLabel(
                row, text=full_label,
                anchor="w", justify="left",
                font=ctk.CTkFont(size=12),
                text_color="#F8FAFC",
                padx=10
            )
            lbl.pack(side="left", fill="x", expand=True)

            def _make_enter(prod, r, t):
                def _on_enter(_):
                    r.configure(fg_color="#374151")
                return _on_enter
            def _make_leave(r):
                def _on_leave(_):
                    r.configure(fg_color="transparent")
                return _on_leave
            on_enter = _make_enter(p, row, full_label)
            on_leave = _make_leave(row)
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            row.bind("<Button-1>", lambda e, prod=p: self._search_dropdown_add(prod))
            lbl.bind("<Button-1>", lambda e, prod=p: self._search_dropdown_add(prod))

        pf_h = pf.winfo_height()
        max_h = max(pf_h - rel_y - 10, 80)
        desired = len(matches) * 34 + 10
        h = max(min(desired, max_h, 350), min(200, desired))
        self._search_dropdown.configure(width=max(w, 50), height=max(h, 30))

        self._search_dropdown.lift()
        self._bind_dropdown_close()

    def _search_dropdown_add(self, product):
        """Add the selected product from the dropdown and clean up."""
        self.add_to_purchase_order(quantity=1, product=product)
        self.search_var.set("")
        self._hide_search_dropdown()
        self.search_entry.focus_set()

    def _hide_search_dropdown(self):
        """Hide the search dropdown."""
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
            if (dx <= event.x_root <= dx + dw and dy <= event.y_root <= dy + dh):
                return
        except Exception:
            pass
        self._hide_search_dropdown()

    def _on_search_keyrelease(self, event=None):
        """Handle typing in the search entry — show dropdown with matches."""
        if event and event.keysym in ("Down", "Up", "Return", "Escape"):
            return
        term = self.search_var.get().strip().lower()
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
        for p in self.all_products:
            if term.lower() in p['name'].lower() or term.lower() in p['sku'].lower():
                self._hide_search_dropdown()
                self._search_dropdown_add(p)
                return
        self._hide_search_dropdown()
        self._open_product_browser(term)

    def _on_search_arrow_down(self, event=None):
        pass

    # ── Barcode ──────────────────────────────────────────────────────

    def _on_barcode_scanned(self, event=None):
        """Barcode scanned — find product and add directly to PO."""
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
            self.barcode_entry.configure(border_color="#ef4444")
            self.barcode_status.configure(text="❌ Not found", text_color="#ef4444")
            self.parent.after(2000, lambda: (
                self.barcode_entry.configure(border_color=("#565b5e", "#949A9F")),
                self.barcode_status.configure(text="")
            ))
            self.barcode_entry.focus_set()
            return
        self.add_to_purchase_order(quantity=1, product=product)
        self.barcode_status.configure(text="✅ Added!", text_color="#22c55e")
        self.parent.after(1500, lambda: self.barcode_status.configure(text=""))
        self.barcode_entry.focus_set()

    # ── Browse Products Modal ────────────────────────────────────────

    def _open_product_browser(self, initial_search=""):
        """Open a modal window to browse and select products."""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Select Products")
        modal.geometry("900x600")
        modal.minsize(600, 400)
        modal.transient(self.parent)
        modal.grab_set()
        modal.resizable(True, True)

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

        search_row = ctk.CTkFrame(modal, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=(10, 6))

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_row, textvariable=search_var,
            placeholder_text="Search by name or SKU...",
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

        tree_frame = ctk.CTkFrame(modal)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=6)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("SKU", "Name", "Stock", "Cost Price")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")

        tree.tag_configure("stock_zero", background="#7F1D1D", foreground="#FFFFFF",
                           font=("Segoe UI", 11, "bold"))
        tree.tag_configure("stock_low", background="#7F1D1D", foreground="#FFFFFF",
                           font=("Segoe UI", 11, "bold"))
        tree.tag_configure("stock_ok", background="#1E293B", foreground="#F8FAFC",
                           font=("Segoe UI", 11))

        col_widths = {"SKU": 90, "Name": 350, "Stock": 100, "Cost Price": 110}
        for col in cols:
            anchor = "w" if col == "Name" else "center"
            tree.heading(col, text=col, anchor=anchor)
            tree.column(col, width=col_widths[col], anchor=anchor, minwidth=60)

        v_sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_sb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)
        v_sb.grid(row=0, column=1, sticky="ns")
        h_sb.grid(row=1, column=0, sticky="ew")

        footer = ctk.CTkFrame(modal, fg_color=("#F8FAFC", "#1E293B"), height=42)
        footer.pack(fill="x", padx=0, pady=0)
        footer.pack_propagate(False)

        count_label = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(size=11))
        count_label.pack(side="left", padx=(12, 0))

        add_btn = ctk.CTkButton(
            footer, text="📋  Add to PO",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32, width=140,
            fg_color="#4CAF50", hover_color="#45A049",
            state="disabled"
        )
        add_btn.pack(side="right", padx=(0, 12))

        _current_filtered = []

        def _populate(product_list):
            nonlocal _current_filtered
            _current_filtered = list(product_list)
            for item in tree.get_children():
                tree.delete(item)
            for idx, p in enumerate(product_list):
                avail = p['stock']
                reorder = p['reorder_level']
                if avail <= 0:
                    tag = "stock_zero"
                elif avail <= reorder:
                    tag = "stock_low"
                else:
                    tag = "stock_ok"
                tree.insert("", "end", values=(
                    p['sku'], p['name'], avail,
                    f"Rs{p['cost_price']:.2f}" if p['cost_price'] else "N/A"
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
                self.add_to_purchase_order(quantity=1, product=product)
                add_btn.configure(text="✅  Added!", fg_color="#10B981")
                modal.after(800, lambda: add_btn.configure(
                    text="📋  Add to PO", fg_color="#4CAF50"
                ))

        def _on_select(_=None):
            sel = tree.selection()
            add_btn.configure(state="normal" if sel else "disabled")

        def _on_double_click(_=None):
            _add_selected()

        def _on_modal_barcode(_=None):
            code = barcode_var.get().strip()
            if not code:
                return
            barcode_var.set("")
            for p in self.all_products:
                if p.get('barcode') and p['barcode'] == code:
                    self.add_to_purchase_order(quantity=1, product=p)
                    add_btn.configure(text="✅  Added!", fg_color="#10B981")
                    modal.after(800, lambda: add_btn.configure(
                        text="📋  Add to PO", fg_color="#4CAF50"
                    ))
                    for item_id in tree.get_children():
                        vals = tree.item(item_id, 'values')
                        if vals and vals[0] == p['sku']:
                            tree.selection_set(item_id)
                            tree.focus(item_id)
                            tree.see(item_id)
                            _on_select()
                            break
                    return
            barcode_entry.configure(border_color="#ef4444")
            modal.after(1500, lambda: barcode_entry.configure(
                border_color=("#565b5e", "#949A9F")
            ))

        search_var.trace('w', _do_filter)
        barcode_entry.bind("<Return>", _on_modal_barcode)
        tree.bind("<<TreeviewSelect>>", _on_select)
        tree.bind("<Double-1>", _on_double_click)
        add_btn.configure(command=_add_selected)
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.protocol("WM_DELETE_WINDOW", modal.destroy)

        if initial_search:
            search_var.set(initial_search)
            _do_filter()
        else:
            _populate(self.all_products)
        search_entry.focus_set()

    def load_suppliers(self):
        """Load suppliers for dropdown"""
        try:
            suppliers = db.execute_query("SELECT supplier_id, name FROM suppliers WHERE is_active = 1")
            supplier_values = ["Select Supplier..."]
            self.suppliers_data = {"Select Supplier...": {"supplier_id": None}}
            
            for supplier in suppliers:
                supplier_values.append(supplier['name'])
                self.suppliers_data[supplier['name']] = {
                    "supplier_id": supplier['supplier_id']
                }
            
            self.supplier_dropdown.configure(values=supplier_values)
            
        except Exception as e:
            print(f"Error loading suppliers: {e}")
    
    def load_products(self):
        """Load products for selection"""
        try:
            query = """
                SELECT p.product_id, p.sku, p.name, p.stock, p.cost_price, p.reorder_level
                FROM products p
                WHERE p.is_active = 1
                ORDER BY p.name
            """
            products = db.execute_query(query)
            self.all_products = products
        except Exception as e:
            print(f"Error loading products: {e}")

    def on_supplier_selected(self, supplier_name):
        """Handle supplier selection"""
        self.current_supplier = self.suppliers_data.get(supplier_name)
        self.update_purchase_order_display()
        self.po_items_scroll.update_idletasks()
    
    def add_to_purchase_order(self, quantity=1, product=None, unit_cost=None):
        """Add a product to the purchase order. Product must be provided."""
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier first.")
            return

        if product is None:
            messagebox.showwarning("Warning", "Please select a product from the search or browse list.")
            return

        if unit_cost is None:
            unit_cost = product.get('cost_price', 0) or 0.0

        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return

        # Check if product already in purchase order
        for item in self.purchase_items:
            if item['product_id'] == product['product_id']:
                item['quantity'] += quantity
                item['unit_cost'] = unit_cost
                self.update_purchase_order_display()
                return

        # New item
        self.purchase_items.append({
            'product_id': product['product_id'],
            'sku': product['sku'],
            'name': product['name'],
            'quantity': quantity,
            'unit_cost': unit_cost
        })
        self.update_purchase_order_display()

    # ── Inline item helpers (sales-style) ─────────────────────────────

    def _inc_po_item(self, index):
        """Increment quantity of PO item at index."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items[index]['quantity'] += 1
            self.update_purchase_order_display()

    def _dec_po_item(self, index):
        """Decrement quantity of PO item at index. Removes item if qty reaches 0."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items[index]['quantity'] -= 1
            if self.purchase_items[index]['quantity'] <= 0:
                self.purchase_items.pop(index)
            self.update_purchase_order_display()

    def _remove_po_item(self, index):
        """Remove PO item at index."""
        if 0 <= index < len(self.purchase_items):
            self.purchase_items.pop(index)
            self.update_purchase_order_display()
    
    def clear_purchase_order(self):
        """Clear all items from purchase order"""
        if self.purchase_items:
            if messagebox.askyesno("Confirm", "Clear all items from purchase order?"):
                self.purchase_items = []
                self.update_purchase_order_display()
    
    def update_purchase_order_display(self):
        """Update cart display — centered empty label or item rows inside po_items_scroll."""
        count = len(self.purchase_items)
        subtotal = 0

        # Destroy item rows but keep po_empty_label
        for w in self.po_items_scroll.winfo_children():
            if w != self.po_empty_label:
                w.destroy()

        if count == 0:
            self.po_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.po_empty_label.place_forget()

            for idx, item in enumerate(self.purchase_items):
                total_cost = item['unit_cost'] * item['quantity']
                subtotal += total_cost

                bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
                is_dark = ctk.get_appearance_mode() == "Dark"
                if is_dark:
                    bg = "#1E1E2E" if idx % 2 == 0 else "#1A1A2E"

                row_frame = ctk.CTkFrame(self.po_items_scroll, fg_color=bg, height=34)
                row_frame.pack(fill="x", padx=1, pady=(0, 1))
                row_frame.pack_propagate(False)

                # Grid weights match header: Product(4) | Qty(1) | Total(1) | UnitCost(1) | Remove(1)
                row_frame.grid_columnconfigure(0, weight=4)
                row_frame.grid_columnconfigure(1, weight=1)
                row_frame.grid_columnconfigure(2, weight=1)
                row_frame.grid_columnconfigure(3, weight=1)
                row_frame.grid_columnconfigure(4, weight=1)

                # Product name (col 0, left-aligned)
                name = item['name'][:22] + ".." if len(item['name']) > 22 else item['name']
                ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=10),
                             anchor="w").grid(row=0, column=0, sticky="w", padx=(8, 4))

                # Qty controls frame (col 1, centered)
                qty_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                qty_frame.grid(row=0, column=1)
                dec_btn = ctk.CTkButton(
                    qty_frame, text="−", width=26, height=24,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    fg_color=("#FF6B35", "#D35400"), hover_color=("#E55A2B", "#B64900"),
                    command=lambda i=idx: self._dec_po_item(i)
                )
                dec_btn.pack(side="left", padx=(2, 1))
                if item['quantity'] <= 1:
                    dec_btn.configure(state="disabled")

                ctk.CTkLabel(qty_frame, text=str(item['quantity']),
                              font=ctk.CTkFont(size=11, weight="bold"), width=22).pack(side="left", padx=(1, 1))

                inc_btn = ctk.CTkButton(
                    qty_frame, text="+", width=26, height=24,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    fg_color=("#2196F3", "#1565C0"), hover_color=("#1976D2", "#0D47A1"),
                    command=lambda i=idx: self._inc_po_item(i)
                )
                inc_btn.pack(side="left", padx=(1, 4))

                # Total label (col 2, right-aligned)
                ctk.CTkLabel(row_frame, text=f"Rs{total_cost:.2f}",
                              font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=2, sticky="e", padx=(0, 4))

                # Unit cost entry (col 3, right-aligned, fixed width 70)
                cost_var = tk.StringVar(value=f"{item['unit_cost']:.2f}")
                cost_entry = ctk.CTkEntry(
                    row_frame, textvariable=cost_var, width=70, height=24,
                    font=ctk.CTkFont(size=10),
                    justify="right",
                    border_width=1,
                    fg_color=("#FFFFFF", "#1E1E2E"),
                    text_color=("#64748B", "#94A3B8")
                )
                cost_entry.grid(row=0, column=3, sticky="e", padx=(0, 4))
                def on_cost_change(e, i=idx, var=cost_var):
                    try:
                        new_cost = float(var.get())
                        if new_cost >= 0:
                            self.purchase_items[i]['unit_cost'] = new_cost
                            self.update_purchase_order_display()
                    except ValueError:
                        pass
                cost_entry.bind("<FocusOut>", on_cost_change)
                cost_entry.bind("<Return>", on_cost_change)

                # Remove button (col 4, right-aligned)
                ctk.CTkButton(
                    row_frame, text="×", width=24, height=22,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color=("#FEE2E2", "#3B0A0A"), hover_color=("#FECACA", "#5B1A1A"),
                    text_color=("#DC2626", "#FCA5A5"),
                    command=lambda i=idx: self._remove_po_item(i)
                ).grid(row=0, column=4, padx=(2, 4), sticky="e")

        # Update summary
        self.subtotal_value.configure(text=f"Rs{subtotal:.2f}")
        self.total_value.configure(text=f"Rs {subtotal:,.2f}")

        # Update badge
        self.po_badge.configure(text=f"({count})")

        # Enable/disable create button
        if count > 0:
            self.create_po_btn.configure(
                text=f"📋 Create Purchase Order — Rs {subtotal:,.2f}",
                state="normal",
                fg_color="#10B981",
                text_color="#FFFFFF",
                hover_color="#059669"
            )
        else:
            self.create_po_btn.configure(
                text="📋 Create Purchase Order",
                state="disabled",
                fg_color="#374151",
                text_color="#9CA3AF",
                hover_color="#374151"
            )

        self.po_items_scroll.update_idletasks()
    
    def create_purchase_order(self):
        """Create the purchase order"""
        if not self.purchase_items:
            messagebox.showwarning("Warning", "Purchase order is empty. Add items first.")
            return
        
        if not self.current_supplier or not self.current_supplier['supplier_id']:
            messagebox.showwarning("Warning", "Please select a supplier.")
            return
        
        try:
            # Generate PO number
            today = datetime.now()
            base_number = f"PO-{today.strftime('%Y%m%d')}"
            
            # Find next number for today
            query = "SELECT COUNT(*) as count FROM purchases WHERE invoice_number LIKE ?"
            result = db.execute_query(query, (f"{base_number}-%",))
            count = result[0]['count'] if result else 0
            
            po_number = f"{base_number}-{count + 1:03d}"
            
            # Calculate totals
            subtotal = sum(item['unit_cost'] * item['quantity'] for item in self.purchase_items)
            
            # Get expected delivery date
            expected_delivery = self.delivery_entry.get() or None
            if expected_delivery:
                try:
                    # Validate date format
                    datetime.strptime(expected_delivery, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                    return
            
            # Create purchase record
            purchase_id = db.execute_insert("""
                INSERT INTO purchases (invoice_number, supplier_id, purchase_date,
                                     payment_method, subtotal, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                po_number,
                self.current_supplier['supplier_id'],
                datetime.now().date(),
                self.payment_var.get().lower(),
                subtotal,
                subtotal,
                'pending',
                f"Expected delivery: {expected_delivery}" if expected_delivery else None
            ))
            
            # Add purchase items
            for item in self.purchase_items:
                total_cost = item['unit_cost'] * item['quantity']
                
                db.execute_insert("""
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    item['product_id'],
                    item['quantity'],
                    item['unit_cost'],
                    total_cost
                ))
            
            # Clear purchase order and refresh
            self.purchase_items = []
            self.update_purchase_order_display()
            self.supplier_var.set("Select Supplier...")
            self.current_supplier = None
            self.delivery_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Purchase order created successfully!\nPO Number: {po_number}")
            
        except Exception as e:
            print(f"Error creating purchase order: {e}")
            messagebox.showerror("Error", f"Failed to create purchase order: {e}")
    
    def load_purchase_history(self):
        """Load purchase history data"""
        try:
            query = """
                SELECT p.id as purchase_id, p.invoice_number as po_number, p.purchase_date, p.notes,
                       p.total_amount, p.status, s.name as supplier_name,
                       COUNT(pi.id) as item_count
                FROM purchases p
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN purchase_items pi ON p.id = pi.purchase_id
                GROUP BY p.id
                ORDER BY p.purchase_date DESC
            """
            purchases = db.execute_query(query)
            
            # Clear existing items
            for item in self.purchase_history_tree.get_children():
                self.purchase_history_tree.delete(item)
            
            # Add purchases to tree
            for purchase in purchases:
                supplier_name = purchase['supplier_name'] or "Unknown Supplier"
                status = purchase['status'].title()
                # Extract expected delivery from notes if available
                notes = purchase['notes'] or ""
                expected_delivery = "Not specified"
                if "Expected delivery:" in notes:
                    try:
                        expected_delivery = notes.split("Expected delivery: ")[1].strip()
                    except:
                        expected_delivery = "Not specified"
                
                self.purchase_history_tree.insert("", "end", values=(
                    purchase['po_number'],
                    purchase['purchase_date'],
                    supplier_name,
                    purchase['item_count'],
                    f"Rs{purchase['total_amount']:.2f}",
                    status,
                    expected_delivery
                ))
            
            self.all_purchase_data = purchases
            
        except Exception as e:
            print(f"Error loading purchase history: {e}")
            messagebox.showerror("Error", f"Failed to load purchase history: {e}")
    
    def filter_purchase_history(self, *args):
        """Filter purchase history based on search"""
        pass  # Simplified for now
    
    def view_purchase_details(self):
        """View detailed information about a selected purchase"""
        messagebox.showinfo("Info", "Purchase details feature coming soon!")
    
    def mark_as_received(self):
        """Mark selected purchase order as received and update stock"""
        selected = self.purchase_history_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a purchase order first.")
            return

        values = self.purchase_history_tree.item(selected[0], "values")
        po_number = values[0]

        # Look up purchase_id from stored data
        purchase_id = None
        for p in self.all_purchase_data:
            if p['po_number'] == po_number:
                purchase_id = p['purchase_id']
                break

        if not purchase_id:
            messagebox.showerror("Error", "Could not find purchase order data.")
            return

        confirm = messagebox.askyesno("Confirm", f"Mark {po_number} as received?\n\nThis will update product stock levels.")
        if not confirm:
            return

        try:
            # Get purchase items
            items = db.execute_query("""
                SELECT product_id, quantity FROM purchase_items WHERE purchase_id = ?
            """, (purchase_id,))

            # Update stock for each item
            for item in items:
                db.execute_update("""
                    UPDATE products SET stock = stock + ? WHERE product_id = ?
                """, (item['quantity'], item['product_id']))

            # Update purchase status
            db.execute_update("""
                UPDATE purchases SET status = 'received' WHERE id = ?
            """, (purchase_id,))

            messagebox.showinfo("Success", f"{po_number} marked as received.\nStock levels updated.")
            self.load_purchase_history()

        except Exception as e:
            print(f"Error marking as received: {e}")
            messagebox.showerror("Error", f"Failed to mark as received: {e}")
    
    def show_add_product_dialog(self, product):
        """Show custom dialog for adding product to purchase order"""
        dialog = AddProductDialog(self.parent, product)
        return dialog.result


class AddProductDialog:
    def __init__(self, parent, product):
        self.parent = parent
        self.product = product
        self.result = None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Add {product['name']} to Purchase Order")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
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
        
        self.create_dialog_content()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_dialog_content(self):
        """Create the dialog content"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product info header
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#e3f2fd", "#1565c0"))
        header_frame.pack(fill="x", padx=15, pady=(15, 20))
        
        product_icon = ctk.CTkLabel(header_frame, text="📦", font=ctk.CTkFont(size=24))
        product_icon.pack(pady=(15, 5))
        
        product_name = ctk.CTkLabel(
            header_frame,
            text=self.product['name'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0d47a1", "white")
        )
        product_name.pack(pady=(0, 5))
        
        product_sku = ctk.CTkLabel(
            header_frame,
            text=f"SKU: {self.product['sku']}",
            font=ctk.CTkFont(size=14),
            text_color=("#1976d2", "#e3f2fd")
        )
        product_sku.pack(pady=(0, 15))
        
        # Input fields - use scrollable frame to ensure all content is visible
        fields_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        fields_frame.pack(fill="both", expand=True, padx=15)
        
        # Quantity field
        qty_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        qty_frame.pack(fill="x", pady=(0, 15))
        
        qty_label = ctk.CTkLabel(
            qty_frame,
            text="📊 Quantity to Order:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        qty_label.pack(pady=(15, 10))
        
        self.quantity_entry = ctk.CTkEntry(
            qty_frame,
            placeholder_text="Enter quantity...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.quantity_entry.pack(padx=20, pady=(0, 15), fill="x")
        
        # Unit cost field
        cost_frame = ctk.CTkFrame(fields_frame, corner_radius=10)
        cost_frame.pack(fill="x", pady=(0, 15))
        
        cost_label = ctk.CTkLabel(
            cost_frame,
            text="💰 Unit Cost (Rs):",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        cost_label.pack(pady=(15, 10))
        
        default_cost = self.product['cost_price'] if self.product['cost_price'] else 0
        self.cost_entry = ctk.CTkEntry(
            cost_frame,
            placeholder_text="Enter unit cost...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.cost_entry.pack(padx=20, pady=(0, 5), fill="x")
        # Insert default cost if available
        if default_cost > 0:
            self.cost_entry.insert(0, str(default_cost))
        else:
            self.cost_entry.insert(0, "0.00")
        
        # Current cost display
        current_cost_label = ctk.CTkLabel(
            cost_frame,
            text=f"Current Cost: Rs{default_cost:.2f}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        current_cost_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
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
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add to Order",
            command=self.add_product,
            width=140,
            height=45,
            corner_radius=10,
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="right")
        
        # Focus on quantity entry
        self.quantity_entry.focus()
    
    def add_product(self):
        """Add product with validation"""
        try:
            # Validate quantity
            quantity_str = self.quantity_entry.get().strip()
            if not quantity_str:
                messagebox.showerror("Error", "Please enter a quantity.")
                return
            
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return
            
            # Validate unit cost
            cost_str = self.cost_entry.get().strip()
            if not cost_str:
                messagebox.showerror("Error", "Please enter a unit cost.")
                return
            
            unit_cost = float(cost_str)
            if unit_cost < 0:
                messagebox.showerror("Error", "Unit cost cannot be negative.")
                return
            
            # Set result and close
            self.result = {
                'quantity': quantity,
                'unit_cost': unit_cost
            }
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and cost.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()
