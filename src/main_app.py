import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import shutil
import json
from datetime import datetime
from PIL import Image

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from models.database import db
from views.dashboard import Dashboard
from views.inventory import InventoryView
from views.sales import SalesView
from views.purchases import PurchasesView
from views.customers import CustomersView
from views.suppliers import SuppliersView
from views.statements import StatementsView
from views.reports import ReportsView
from views.settings import SettingsView
from utils.logger import logger
# Table styles are now handled individually in each view

class InventoryApp:
    def __init__(self):
        # Load saved theme preference
        settings_path = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")
        saved_theme = "dark"
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                saved_theme = settings.get("appearance", {}).get("mode", "dark")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.theme_mode = saved_theme if saved_theme in ("light", "dark") else "dark"

        # Set appearance mode and color theme
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Inventory Beta - Management System")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size based on screen (80% of screen size, max 1600x1000)
        window_width = min(int(screen_width * 0.85), 1600)
        window_height = min(int(screen_height * 0.85), 1000)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set minimum size based on screen (for smaller laptops)
        min_width = max(800, int(screen_width * 0.6))
        min_height = max(500, int(screen_height * 0.6))
        self.root.minsize(min_width, min_height)
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Set window icon based on theme
        self._set_theme_icon()

        # Initialize variables
        self.current_view = None
        
        # Table styles are now handled individually by each view
        
        # Create UI
        self.create_main_layout()
        self.create_sidebar()
        self.create_header()
        self.create_content_area()
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_main_layout(self):
        """Create the main layout with sidebar and content area"""
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Sidebar width based on screen size
        screen_width = self.root.winfo_screenwidth()
        self.sidebar_width = 260 if screen_width < 1400 else 280
        self.sidebar_collapsed = False
        
        # Create main frames
        self.sidebar_frame = ctk.CTkFrame(self.root, width=self.sidebar_width, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # Configure sidebar grid
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=1, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        
        # Bind resize event for responsive behavior
        self.root.bind('<Configure>', self.on_window_resize)
    
    def create_sidebar(self):
        """Create sidebar navigation with improved layout"""
        # Main container for sidebar content
        sidebar_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        sidebar_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        sidebar_container.grid_columnconfigure(0, weight=1)
        sidebar_container.grid_rowconfigure(1, weight=1)  # Nav section expands
        sidebar_container.grid_rowconfigure(2, weight=0)    # Bottom section fixed
        
        # Logo and title section
        logo_frame = ctk.CTkFrame(sidebar_container, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Add a logo icon label
        logo_icon = ctk.CTkLabel(
            logo_frame,
            text="📦",
            font=ctk.CTkFont(size=32)
        )
        logo_icon.pack()
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="INVENTORY BETA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Management System",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        subtitle_label.pack()
        
        # Navigation section (scrollable for small screens)
        nav_container = ctk.CTkFrame(sidebar_container, fg_color="transparent")
        nav_container.grid(row=1, column=0, sticky="nsew", pady=10)
        nav_container.grid_columnconfigure(0, weight=1)
        nav_container.grid_rowconfigure(0, weight=1)
        
        # Navigation buttons frame
        nav_frame = ctk.CTkFrame(nav_container, fg_color="transparent")
        nav_frame.grid(row=0, column=0, sticky="new")
        nav_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation items with icons (store both display text and key)
        nav_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📦 Inventory", self.show_inventory),
            ("💰 Sales", self.show_sales),
            ("🛒 Purchases", self.show_purchases),
            ("👥 Customers", self.show_customers),
            ("🏭 Suppliers", self.show_suppliers),
            ("📋 Statements", self.show_statements),
            ("📊 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings),
        ]
        
        self.nav_buttons = {}
        for i, (text, command) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                height=42,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                border_spacing=10
            )
            btn.grid(row=i, column=0, sticky="ew", pady=3, padx=5)
            self.nav_buttons[text] = btn
        
        # Bottom section with separator
        bottom_container = ctk.CTkFrame(sidebar_container, fg_color="transparent")
        bottom_container.grid(row=2, column=0, sticky="sew", pady=(15, 0))
        bottom_container.grid_columnconfigure(0, weight=1)
        
        # Separator line
        separator = ctk.CTkFrame(bottom_container, height=2, fg_color=("gray70", "gray40"))
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Backup button
        backup_btn = ctk.CTkButton(
            bottom_container,
            text="💾   Backup Database",
            command=self.backup_database,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#3B82F6", "#2563EB"),
            hover_color=("#2563EB", "#1d4ed8"),
            corner_radius=8,
            anchor="w"
        )
        backup_btn.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=5)

        # Theme toggle frame
        theme_frame = ctk.CTkFrame(bottom_container, fg_color="transparent")
        theme_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="☀️ Light Mode" if self.theme_mode == "light" else "🌙   Dark Mode",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12),
            progress_color=("#3B82F6", "#60A5FA")
        )
        self.theme_switch.pack(side="left", padx=10)
        self.theme_switch.select() if self.theme_mode == "dark" else self.theme_switch.deselect()
    
    def create_header(self):
        """Create header with user info and actions"""
        # Configure header grid
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Current view title
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.header_title.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        # Current date/time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.datetime_label = ctk.CTkLabel(
            self.header_frame,
            text=f"📅 {current_time}",
            font=ctk.CTkFont(size=12)
        )
        self.datetime_label.grid(row=0, column=2, sticky="e", padx=20, pady=20)
        
        # Update time every minute
        self.update_datetime()
    
    def create_content_area(self):
        """Create the main content area"""
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def update_datetime(self):
        """Update the datetime display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.datetime_label.configure(text=f"📅 {current_time}")
        self.root.after(60000, self.update_datetime)  # Update every minute
    
    def clear_content(self):
        """Clear the current content with smooth fade effect"""
        # Store current view for transition
        current_widgets = self.content_frame.winfo_children()
        
        # Fade out effect
        if current_widgets:
            try:
                # Gradually reduce opacity (simulated by hiding with delay)
                for widget in current_widgets:
                    widget.update()
            except:
                pass
        
        # Clear widgets
        for widget in current_widgets:
            try:
                widget.destroy()
            except:
                pass
        
        # Reset nav button colors
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        
        # Small delay for smooth transition
        self.root.update_idletasks()
    
    def set_active_nav(self, text):
        """Set the active navigation button"""
        for btn_text, btn in self.nav_buttons.items():
            if btn_text == text:
                btn.configure(
                    fg_color=("#3B82F6", "#1d4ed8"),
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_content()
        self.header_title.configure(text="Dashboard")
        self.set_active_nav("🏠 Dashboard")
        
        # Pass navigation callbacks to Dashboard for quick actions
        navigation_callbacks = {
            'inventory': self.show_inventory,
            'sales': self.show_sales,
            'purchases': self.show_purchases,
            'customers': self.show_customers
        }
        
        self.current_view = Dashboard(self.content_frame, navigation_callbacks)
    
    def show_inventory(self):
        """Show inventory view"""
        self.clear_content()
        self.header_title.configure(text="Inventory Management")
        self.set_active_nav("📦 Inventory")
        
        self.current_view = InventoryView(self.content_frame)
    
    def show_sales(self):
        """Show sales view"""
        self.clear_content()
        self.header_title.configure(text="Sales Management")
        self.set_active_nav("💰 Sales")
        
        self.current_view = SalesView(self.content_frame)
    
    def show_purchases(self):
        """Show purchases view"""
        self.clear_content()
        self.header_title.configure(text="Purchase Management")
        self.set_active_nav("🛒 Purchases")
        
        self.current_view = PurchasesView(self.content_frame)
    
    def show_customers(self):
        """Show customers view"""
        self.clear_content()
        self.header_title.configure(text="Customer Management")
        self.set_active_nav("👥 Customers")
        
        self.current_view = CustomersView(self.content_frame)
    
    def show_suppliers(self):
        """Show suppliers view"""
        self.clear_content()
        self.header_title.configure(text="Supplier Management")
        self.set_active_nav("🏭 Suppliers")
        
        self.current_view = SuppliersView(self.content_frame)
    
    def show_reports(self):
        """Show reports view"""
        self.clear_content()
        self.header_title.configure(text="Reports & Analytics")
        self.set_active_nav("📊 Reports")
        
        self.current_view = ReportsView(self.content_frame)
    
    def show_statements(self):
        """Show statements view"""
        self.clear_content()
        self.header_title.configure(text="Financial Statements")
        self.set_active_nav("📋 Statements")
        
        self.current_view = StatementsView(self.content_frame)
    
    def show_settings(self):
        """Show settings view"""
        self.clear_content()
        self.header_title.configure(text="Settings & Preferences")
        self.set_active_nav("⚙️ Settings")
        
        self.current_view = SettingsView(self.content_frame)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        # Remember which view is currently active
        active_nav = None
        for btn_text, btn in self.nav_buttons.items():
            if btn.cget("fg_color") not in ("transparent", ["transparent", "transparent"]):
                active_nav = btn_text
                break

        if self.theme_mode == "dark":
            self.theme_mode = "light"
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="☀️ Light Mode")
        else:
            self.theme_mode = "dark"
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="🌙 Dark Mode")

        # Persist theme preference
        self._save_theme(self.theme_mode)

        # Re-apply active nav styling so text_color is correct after theme change
        if active_nav:
            self.set_active_nav(active_nav)
        else:
            for btn in self.nav_buttons.values():
                btn.configure(text_color=("gray10", "gray90"))
        self._set_theme_icon()

    def _save_theme(self, mode):
        """Save theme preference to settings.json."""
        settings_path = os.path.join(os.path.dirname(__file__), "..", "data", "settings.json")
        try:
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
            if "appearance" not in settings:
                settings["appearance"] = {}
            settings["appearance"]["mode"] = mode
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception:
            pass

    def _set_theme_icon(self):
        """Set window icon based on current theme (Dark/Light)."""
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
            suffix = "dark" if is_dark else "light"
            ico_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", f"app_icon_{suffix}.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(default=ico_path)
            else:
                png_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", f"app_icon_{suffix}.png")
                if os.path.exists(png_path):
                    from PIL import ImageTk
                    icon_image = Image.open(png_path)
                    self._icon_img = ImageTk.PhotoImage(icon_image)
                    self.root.iconphoto(True, self._icon_img)
        except Exception as e:
            print(f"Could not load theme icon: {e}")

    def backup_database(self):
        """Backup the database to a user-chosen location."""
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "inventory.db"))
        if not os.path.exists(db_path):
            messagebox.showerror("Error", f"Database file not found:\n{db_path}")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"inventory_backup_{timestamp}.db"

        dest = filedialog.asksaveasfilename(
            title="Save Database Backup",
            initialfile=default_name,
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not dest:
            return  # User cancelled

        try:
            shutil.copy2(db_path, dest)
            messagebox.showinfo(
                "Backup Successful",
                f"✅ Database backed up successfully!\n\nSaved to:\n{dest}"
            )
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Failed to backup database:\n{e}")

    def on_window_resize(self, event=None):
        """Handle window resize for responsive behavior"""
        if event and event.widget == self.root:
            current_width = event.width
            
            # Auto-collapse sidebar on very small windows
            if current_width < 1000 and not self.sidebar_collapsed:
                self.toggle_sidebar()
            elif current_width >= 1200 and self.sidebar_collapsed:
                self.toggle_sidebar()
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility for small screens"""
        if self.sidebar_collapsed:
            # Expand sidebar
            self.sidebar_frame.grid()
            self.sidebar_frame.configure(width=self.sidebar_width)
            self.sidebar_collapsed = False
        else:
            # Collapse sidebar (hide it)
            self.sidebar_frame.grid_remove()
            self.sidebar_collapsed = True
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = InventoryApp()
    app.run()
