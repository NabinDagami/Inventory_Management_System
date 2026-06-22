#!/usr/bin/env python3
"""
Inventory Pro - Professional Inventory Management System
Author: AI Assistant
Version: 1.1.0
"""

import sys
import os
import traceback

# Get the base directory (works for both script and PyInstaller executable)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = os.path.dirname(sys.executable)
    # In PyInstaller, _internal contains the bundled files
    internal_dir = os.path.join(os.path.dirname(sys.executable), '_internal')
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    internal_dir = base_dir

# Add src directory to path
src_path = os.path.join(internal_dir, 'src')
if os.path.exists(src_path):
    sys.path.insert(0, internal_dir)
    sys.path.insert(0, src_path)

def main():
    """Main entry point for the application"""
    try:
        from main_app import InventoryApp
        
        # Create and run the application
        app = InventoryApp()
        app.run()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\nPlease ensure all required packages are installed.")
        print("Run: pip install -r requirements.txt")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"Application Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
