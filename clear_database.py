#!/usr/bin/env python3
"""
Database Clear Script
Removes all data from the inventory management database while preserving table structure.
"""

import sqlite3
import os
import sys
from datetime import datetime

def clear_database():
    """Clear all data from the database tables using our database module"""
    
    try:
        # Import our database module
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from models.database import db
        
        print("🗄️  Connected to database using application module")
        print("🧹 Starting data cleanup...")
        
        # Get all table names from the database
        all_tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        
        if not all_tables:
            print("⚠️  No tables found in database")
            return True
            
        print(f"📊 Found {len(all_tables)} tables")
        
        # Clear tables in proper order to handle foreign key constraints
        tables_to_clear = [
            'sale_items',          # Clear child tables first
            'purchase_items', 
            'stock_movements',
            'sales',               # Then parent tables
            'purchases',
            'products',            # Then referenced tables
            'customers',
            'suppliers',
            'categories',
            'brands',
            'users'                # Finally users
        ]
        
        # Add any additional tables we might have missed
        existing_table_names = [table['name'] for table in all_tables]
        for table_info in all_tables:
            table_name = table_info['name']
            if table_name not in tables_to_clear:
                tables_to_clear.append(table_name)
        
        cleared_count = 0
        
        for table in tables_to_clear:
            if table in existing_table_names:
                try:
                    # Get count before clearing
                    count_result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                    count = count_result[0]['count'] if count_result else 0
                    
                    if count > 0:
                        # Clear the table
                        db.execute_update(f"DELETE FROM {table}")
                        print(f"  ✅ Cleared {count} records from '{table}'")
                        cleared_count += count
                    else:
                        print(f"  ⚪ Table '{table}' was already empty")
                        
                except Exception as e:
                    print(f"  ❌ Error clearing table '{table}': {e}")
            
        # Reset auto-increment sequences if sqlite_sequence exists
        try:
            db.execute_update("DELETE FROM sqlite_sequence")
            print("  🔄 Reset auto-increment sequences")
        except:
            print("  ℹ️  No auto-increment sequences to reset")
        
        print(f"\n🎉 Database cleared successfully!")
        print(f"📊 Total records removed: {cleared_count}")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import database module: {e}")
        print("💡 Make sure you're running this from the project root directory")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def confirm_clear():
    """Ask for user confirmation before clearing database"""
    print("⚠️  WARNING: This will remove ALL DATA from the inventory management database!")
    print("📋 This includes:")
    print("   - All products and inventory")
    print("   - All customers and suppliers") 
    print("   - All sales and purchase records")
    print("   - All users and categories")
    print("   - All transaction history")
    print("\n🔄 The database structure will be preserved (tables and columns remain)")
    
    while True:
        response = input("\n❓ Are you sure you want to proceed? (yes/no): ").lower().strip()
        
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def main():
    """Main function"""
    print("🗂️  Inventory Management Database Cleaner")
    print("=" * 50)
    
    # Get confirmation
    if not confirm_clear():
        print("❌ Operation cancelled by user")
        return
    
    print("\n🚀 Starting database clear operation...")
    
    # Clear the database
    if clear_database():
        print("\n✅ Database cleared successfully!")
        print("💡 You can now add fresh data to your inventory system")
    else:
        print("\n❌ Failed to clear database")
        sys.exit(1)

if __name__ == "__main__":
    main()
