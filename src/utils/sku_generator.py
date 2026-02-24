import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db

class SKUGenerator:
    """Auto-generate SKUs in format CAT-BRAND-001"""
    
    @staticmethod
    def generate_sku(category_id, brand_id):
        """Generate a new SKU based on category and brand"""
        try:
            # Get category name
            category_query = "SELECT category_name FROM categories WHERE category_id = ?"
            category_result = db.execute_query(category_query, (category_id,))
            if not category_result:
                raise ValueError("Category not found")
            category_name = category_result[0]['category_name']
            
            # Get brand name  
            brand_query = "SELECT brand_name FROM brands WHERE brand_id = ?"
            brand_result = db.execute_query(brand_query, (brand_id,))
            if not brand_result:
                raise ValueError("Brand not found")
            brand_name = brand_result[0]['brand_name']
            
            # Create base SKU
            category_short = category_name[:3].upper()
            brand_short = brand_name[:3].upper()
            base_sku = f"{category_short}-{brand_short}"
            
            # Find next available number
            existing_query = """
                SELECT sku FROM products 
                WHERE sku LIKE ? 
                ORDER BY sku DESC LIMIT 1
            """
            existing_result = db.execute_query(existing_query, (f"{base_sku}-%",))
            
            if existing_result:
                # Extract number from last SKU
                last_sku = existing_result[0]['sku']
                try:
                    last_number = int(last_sku.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1
            
            # Format final SKU
            final_sku = f"{base_sku}-{next_number:03d}"
            
            # Ensure uniqueness
            while SKUGenerator.sku_exists(final_sku):
                next_number += 1
                final_sku = f"{base_sku}-{next_number:03d}"
            
            return final_sku
            
        except Exception as e:
            # Fallback to timestamp-based SKU
            import time
            timestamp = int(time.time())
            return f"PRD-{timestamp}"
    
    @staticmethod
    def sku_exists(sku):
        """Check if SKU already exists"""
        query = "SELECT COUNT(*) as count FROM products WHERE sku = ?"
        result = db.execute_query(query, (sku,))
        return result[0]['count'] > 0 if result else False
    
    @staticmethod
    def validate_sku(sku):
        """Validate SKU format"""
        if not sku or len(sku) < 3:
            return False
        
        # Check if it matches expected pattern
        parts = sku.split('-')
        if len(parts) < 2:
            return False
            
        return True
