import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.database import db

def add_sample_purchases():
    """Add sample purchase data"""
    
    # Get supplier and product data
    suppliers = db.execute_query("SELECT supplier_id, name FROM suppliers WHERE is_active = 1 LIMIT 3")
    products = db.execute_query("SELECT product_id, name, cost_price FROM products WHERE is_active = 1 LIMIT 8")
    
    if not suppliers or not products:
        print("No suppliers or products found. Please add suppliers and products first.")
        return
    
    print(f"Found {len(suppliers)} suppliers and {len(products)} products")
    
    # Create sample purchases
    sample_purchases = [
        {
            'invoice_number': 'PO-20250901-001',
            'supplier_id': suppliers[0]['supplier_id'],
            'purchase_date': '2025-09-01',
            'status': 'completed',
            'notes': 'Expected delivery: 2025-09-05',
            'items': [
                {'product_id': products[0]['product_id'], 'quantity': 20, 'unit_price': products[0]['cost_price'] or 15},
                {'product_id': products[1]['product_id'], 'quantity': 10, 'unit_price': products[1]['cost_price'] or 12},
            ]
        },
        {
            'invoice_number': 'PO-20250902-001',
            'supplier_id': suppliers[1]['supplier_id'],
            'purchase_date': '2025-09-02',
            'status': 'pending',
            'notes': 'Expected delivery: 2025-09-08',
            'items': [
                {'product_id': products[2]['product_id'], 'quantity': 15, 'unit_price': products[2]['cost_price'] or 8},
                {'product_id': products[3]['product_id'], 'quantity': 25, 'unit_price': products[3]['cost_price'] or 10},
                {'product_id': products[4]['product_id'], 'quantity': 5, 'unit_price': products[4]['cost_price'] or 20},
            ]
        },
        {
            'invoice_number': 'PO-20250903-001',
            'supplier_id': suppliers[2]['supplier_id'],
            'purchase_date': '2025-09-03',
            'status': 'received',
            'notes': 'Expected delivery: 2025-09-06',
            'items': [
                {'product_id': products[5]['product_id'], 'quantity': 30, 'unit_price': products[5]['cost_price'] or 5},
                {'product_id': products[6]['product_id'], 'quantity': 12, 'unit_price': products[6]['cost_price'] or 18},
            ]
        }
    ]
    
    try:
        for purchase_data in sample_purchases:
            # Calculate totals
            subtotal = sum(item['unit_price'] * item['quantity'] for item in purchase_data['items'])
            
            # Create purchase record
            purchase_id = db.execute_insert("""
                INSERT INTO purchases (invoice_number, supplier_id, purchase_date,
                                     subtotal, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                purchase_data['invoice_number'],
                purchase_data['supplier_id'],
                purchase_data['purchase_date'],
                subtotal,
                subtotal,
                purchase_data['status'],
                purchase_data['notes']
            ))
            
            print(f"Created purchase: {purchase_data['invoice_number']} (ID: {purchase_id})")
            
            # Add purchase items
            for item in purchase_data['items']:
                total_cost = item['unit_price'] * item['quantity']
                
                db.execute_insert("""
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    item['product_id'],
                    item['quantity'],
                    item['unit_price'],
                    total_cost
                ))
                
                # Get product name for display
                product_name = next(p['name'] for p in products if p['product_id'] == item['product_id'])
                print(f"  - Added item: {product_name} x{item['quantity']} @ Rs{item['unit_price']:.2f}")
        
        print("Sample purchase data added successfully!")
        
        # Verify data was added
        count = db.execute_query("SELECT COUNT(*) as count FROM purchases")[0]['count']
        print(f"Total purchases in database: {count}")
        
    except Exception as e:
        print(f"Error adding sample purchases: {e}")

if __name__ == "__main__":
    add_sample_purchases()
