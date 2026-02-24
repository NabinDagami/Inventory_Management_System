import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class SettingsView:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "settings.json")
        self.settings = self.load_settings()
        self.create_settings_view()
    
    def load_settings(self):
        """Load settings from JSON file or create defaults"""
        default_settings = {
            "company": {
                "name": "Your Company Name",
                "address": "",
                "phone": "",
                "email": "",
                "logo_path": ""
            },
            "defaults": {
                "currency": "Rs",
                "tax_rate": 0.0,
                "payment_terms": 30,
                "default_reorder_level": 10
            },
            "inventory": {
                "low_stock_threshold": 10,
                "enable_negative_stock": False
            },
            "notifications": {
                "enable_low_stock_alerts": True,
                "alert_check_interval": 5  # minutes
            },
            "backup": {
                "auto_backup": False,
                "backup_interval": 7,  # days
                "backup_location": ""
            }
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_settings.items():
                        if key not in saved_settings:
                            saved_settings[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in saved_settings[key]:
                                    saved_settings[key][sub_key] = sub_value
                    return saved_settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return default_settings
        return default_settings
    
    def save_settings_to_file(self):
        """Save settings to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False
    
    def create_settings_view(self):
        """Create the settings interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Settings & Preferences",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=15)
        
        # Save button
        save_btn = ctk.CTkButton(
            header_frame,
            text="💾 Save All Settings",
            command=self.save_all_settings,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        save_btn.pack(side="right", padx=10, pady=10)
        
        # Create scrollable content
        content_frame = ctk.CTkScrollableFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Company Information Section
        self.create_company_section(content_frame)
        
        # Default Settings Section
        self.create_defaults_section(content_frame)
        
        # Inventory Settings Section
        self.create_inventory_section(content_frame)
        
        # Notifications Section
        self.create_notifications_section(content_frame)
        
        # Backup Settings Section
        self.create_backup_section(content_frame)
    
    def create_section_frame(self, parent, title, icon):
        """Create a collapsible section frame"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", padx=0, pady=0)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_label.pack(side="left", padx=15, pady=10)
        
        # Content frame
        content = ctk.CTkFrame(section_frame)
        content.pack(fill="x", padx=10, pady=10)
        
        return content
    
    def create_company_section(self, parent):
        """Create company information section"""
        content = self.create_section_frame(parent, "Company Information", "🏢")
        
        # Company Name
        row = 0
        ctk.CTkLabel(content, text="Company Name:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.company_name_entry = ctk.CTkEntry(content, width=350)
        self.company_name_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.company_name_entry.insert(0, self.settings["company"]["name"])
        
        # Address
        row += 1
        ctk.CTkLabel(content, text="Address:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.address_text = ctk.CTkTextbox(content, width=350, height=60)
        self.address_text.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.address_text.insert("1.0", self.settings["company"]["address"])
        
        # Phone
        row += 1
        ctk.CTkLabel(content, text="Phone:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.phone_entry = ctk.CTkEntry(content, width=350)
        self.phone_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.phone_entry.insert(0, self.settings["company"]["phone"])
        
        # Email
        row += 1
        ctk.CTkLabel(content, text="Email:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.email_entry = ctk.CTkEntry(content, width=350)
        self.email_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.email_entry.insert(0, self.settings["company"]["email"])
        
        # Logo
        row += 1
        ctk.CTkLabel(content, text="Logo:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        logo_frame = ctk.CTkFrame(content)
        logo_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        
        self.logo_path_label = ctk.CTkLabel(logo_frame, text=self.settings["company"]["logo_path"] or "No logo selected", font=ctk.CTkFont(size=11))
        self.logo_path_label.pack(side="left", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(logo_frame, text="Browse...", command=self.browse_logo, width=80, height=28)
        browse_btn.pack(side="left")
        
        clear_logo_btn = ctk.CTkButton(logo_frame, text="Clear", command=self.clear_logo, width=60, height=28, fg_color="gray")
        clear_logo_btn.pack(side="left", padx=(5, 0))
    
    def create_defaults_section(self, parent):
        """Create default settings section"""
        content = self.create_section_frame(parent, "Default Values", "📋")
        
        # Currency
        row = 0
        ctk.CTkLabel(content, text="Currency Symbol:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.currency_entry = ctk.CTkEntry(content, width=150)
        self.currency_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.currency_entry.insert(0, self.settings["defaults"]["currency"])
        
        # Tax Rate
        row += 1
        ctk.CTkLabel(content, text="Default Tax Rate (%):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        tax_frame = ctk.CTkFrame(content)
        tax_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.tax_rate_entry = ctk.CTkEntry(tax_frame, width=100)
        self.tax_rate_entry.pack(side="left")
        self.tax_rate_entry.insert(0, str(self.settings["defaults"]["tax_rate"]))
        ctk.CTkLabel(tax_frame, text="%", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 0))
        
        # Payment Terms
        row += 1
        ctk.CTkLabel(content, text="Default Payment Terms:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        terms_frame = ctk.CTkFrame(content)
        terms_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.payment_terms_entry = ctk.CTkEntry(terms_frame, width=100)
        self.payment_terms_entry.pack(side="left")
        self.payment_terms_entry.insert(0, str(self.settings["defaults"]["payment_terms"]))
        ctk.CTkLabel(terms_frame, text="days", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 0))
        
        # Default Reorder Level
        row += 1
        ctk.CTkLabel(content, text="Default Reorder Level:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.reorder_level_entry = ctk.CTkEntry(content, width=150)
        self.reorder_level_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.reorder_level_entry.insert(0, str(self.settings["defaults"]["default_reorder_level"]))
    
    def create_inventory_section(self, parent):
        """Create inventory settings section"""
        content = self.create_section_frame(parent, "Inventory Settings", "📦")
        
        # Low Stock Threshold
        row = 0
        ctk.CTkLabel(content, text="Low Stock Alert Threshold:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.low_stock_threshold_entry = ctk.CTkEntry(content, width=150)
        self.low_stock_threshold_entry.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.low_stock_threshold_entry.insert(0, str(self.settings["inventory"]["low_stock_threshold"]))
        
        # Enable Negative Stock
        row += 1
        ctk.CTkLabel(content, text="Allow Negative Stock:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.negative_stock_switch = ctk.CTkSwitch(content, text="", onvalue=True, offvalue=False)
        self.negative_stock_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        if self.settings["inventory"]["enable_negative_stock"]:
            self.negative_stock_switch.select()
    
    def create_notifications_section(self, parent):
        """Create notifications settings section"""
        content = self.create_section_frame(parent, "Notifications", "🔔")
        
        # Enable Low Stock Alerts
        row = 0
        ctk.CTkLabel(content, text="Enable Low Stock Alerts:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.alerts_switch = ctk.CTkSwitch(content, text="", onvalue=True, offvalue=False)
        self.alerts_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        if self.settings["notifications"]["enable_low_stock_alerts"]:
            self.alerts_switch.select()
        
        # Check Interval
        row += 1
        ctk.CTkLabel(content, text="Check Interval:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        interval_frame = ctk.CTkFrame(content)
        interval_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.check_interval_entry = ctk.CTkEntry(interval_frame, width=100)
        self.check_interval_entry.pack(side="left")
        self.check_interval_entry.insert(0, str(self.settings["notifications"]["alert_check_interval"]))
        ctk.CTkLabel(interval_frame, text="minutes", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 0))
    
    def create_backup_section(self, parent):
        """Create backup settings section"""
        content = self.create_section_frame(parent, "Backup Settings", "💾")
        
        # Auto Backup
        row = 0
        ctk.CTkLabel(content, text="Enable Auto Backup:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.auto_backup_switch = ctk.CTkSwitch(content, text="", onvalue=True, offvalue=False)
        self.auto_backup_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        if self.settings["backup"]["auto_backup"]:
            self.auto_backup_switch.select()
        
        # Backup Interval
        row += 1
        ctk.CTkLabel(content, text="Backup Interval:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        interval_frame = ctk.CTkFrame(content)
        interval_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        self.backup_interval_entry = ctk.CTkEntry(interval_frame, width=100)
        self.backup_interval_entry.pack(side="left")
        self.backup_interval_entry.insert(0, str(self.settings["backup"]["backup_interval"]))
        ctk.CTkLabel(interval_frame, text="days", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 0))
        
        # Backup Location
        row += 1
        ctk.CTkLabel(content, text="Backup Location:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        location_frame = ctk.CTkFrame(content)
        location_frame.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        
        self.backup_location_label = ctk.CTkLabel(location_frame, text=self.settings["backup"]["backup_location"] or "Default (data folder)", font=ctk.CTkFont(size=11))
        self.backup_location_label.pack(side="left", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(location_frame, text="Browse...", command=self.browse_backup_location, width=80, height=28)
        browse_btn.pack(side="left")
    
    def browse_logo(self):
        """Browse for company logo"""
        file_path = filedialog.askopenfilename(
            title="Select Company Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.logo_path_label.configure(text=file_path)
    
    def clear_logo(self):
        """Clear the logo selection"""
        self.logo_path_label.configure(text="No logo selected")
    
    def browse_backup_location(self):
        """Browse for backup location"""
        folder_path = filedialog.askdirectory(title="Select Backup Location")
        if folder_path:
            self.backup_location_label.configure(text=folder_path)
    
    def save_all_settings(self):
        """Save all settings"""
        try:
            # Company settings
            self.settings["company"]["name"] = self.company_name_entry.get().strip()
            self.settings["company"]["address"] = self.address_text.get("1.0", "end-1c").strip()
            self.settings["company"]["phone"] = self.phone_entry.get().strip()
            self.settings["company"]["email"] = self.email_entry.get().strip()
            logo_text = self.logo_path_label.cget("text")
            self.settings["company"]["logo_path"] = logo_text if logo_text != "No logo selected" else ""
            
            # Default settings
            self.settings["defaults"]["currency"] = self.currency_entry.get().strip() or "Rs"
            try:
                self.settings["defaults"]["tax_rate"] = float(self.tax_rate_entry.get() or 0)
            except ValueError:
                self.settings["defaults"]["tax_rate"] = 0
            try:
                self.settings["defaults"]["payment_terms"] = int(self.payment_terms_entry.get() or 30)
            except ValueError:
                self.settings["defaults"]["payment_terms"] = 30
            try:
                self.settings["defaults"]["default_reorder_level"] = int(self.reorder_level_entry.get() or 10)
            except ValueError:
                self.settings["defaults"]["default_reorder_level"] = 10
            
            # Inventory settings
            try:
                self.settings["inventory"]["low_stock_threshold"] = int(self.low_stock_threshold_entry.get() or 10)
            except ValueError:
                self.settings["inventory"]["low_stock_threshold"] = 10
            self.settings["inventory"]["enable_negative_stock"] = bool(self.negative_stock_switch.get())
            
            # Notifications settings
            self.settings["notifications"]["enable_low_stock_alerts"] = bool(self.alerts_switch.get())
            try:
                self.settings["notifications"]["alert_check_interval"] = int(self.check_interval_entry.get() or 5)
            except ValueError:
                self.settings["notifications"]["alert_check_interval"] = 5
            
            # Backup settings
            self.settings["backup"]["auto_backup"] = bool(self.auto_backup_switch.get())
            try:
                self.settings["backup"]["backup_interval"] = int(self.backup_interval_entry.get() or 7)
            except ValueError:
                self.settings["backup"]["backup_interval"] = 7
            backup_text = self.backup_location_label.cget("text")
            self.settings["backup"]["backup_location"] = backup_text if backup_text != "Default (data folder)" else ""
            
            # Save to file
            if self.save_settings_to_file():
                messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    @staticmethod
    def get_settings():
        """Static method to get current settings from anywhere in the app"""
        settings_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "settings.json")
        default_settings = {
            "company": {"name": "Your Company Name", "address": "", "phone": "", "email": "", "logo_path": ""},
            "defaults": {"currency": "Rs", "tax_rate": 0.0, "payment_terms": 30, "default_reorder_level": 10},
            "inventory": {"low_stock_threshold": 10, "enable_negative_stock": False},
            "notifications": {"enable_low_stock_alerts": True, "alert_check_interval": 5},
            "backup": {"auto_backup": False, "backup_interval": 7, "backup_location": ""}
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                return default_settings
        return default_settings