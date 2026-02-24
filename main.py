#!/usr/bin/env python3
"""
Inventory Pro - Professional Inventory Management System
Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application"""
    try:
        from src.main_app import InventoryApp
        
        # Create and run the application
        app = InventoryApp()
        app.run()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please ensure all required packages are installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Application Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
