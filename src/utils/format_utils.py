"""
Utility functions for formatting values consistently across the application
"""

import json
import os

def get_currency_symbol():
    """
    Get the currency symbol from settings.json
    
    Returns:
        str: Currency symbol (e.g., "Rs", "$", "€")
    """
    try:
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'settings.json')
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            return settings.get('defaults', {}).get('currency', 'Rs')
    except Exception:
        return 'Rs'


def format_price(price):
    """
    Format price with comma separators like inventory
    Format: Rs 1,800 (no decimal places)
    
    Args:
        price: Numeric value to format
        
    Returns:
        str: Formatted price string (e.g., "Rs 1,800")
    """
    try:
        if price is None:
            price = 0
        currency = get_currency_symbol()
        return f"{currency} {price:,.0f}"
    except (ValueError, TypeError):
        return f"{get_currency_symbol()} 0"


def format_price_with_decimals(price):
    """
    Format price with comma separators and 2 decimal places
    Format: Rs 1,800.00
    
    Args:
        price: Numeric value to format
        
    Returns:
        str: Formatted price string (e.g., "Rs 1,800.00")
    """
    try:
        if price is None:
            price = 0
        currency = get_currency_symbol()
        return f"{currency} {price:,.2f}"
    except (ValueError, TypeError):
        return f"{get_currency_symbol()} 0.00"
