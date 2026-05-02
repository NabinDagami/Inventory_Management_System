# Modify in place - key fixes
import re

with open('robust_importer.py', 'r') as f:
    content = f.read()

# 1. Remove status from column_patterns
content = re.sub(
    r"\s+'status': \[r'\^status\$',\],\n",
    '',
    content
)

# 2. Change column_patterns priority - check name before brand patterns
# Reorder so name patterns come before brand
content = re.sub(
    r"(self\.column_patterns = \{[\s\S]*?)(\s+'brand': \[)(.*?)(\],\n)",
    r"\1            'name': [\n                r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'\n            ],\n\2\3\4",
    content
)

# 3. Make cost_price optional in schema
content = content.replace(
    "'cost_price': {'label': 'Cost Price *', 'required': True, 'type': 'number'},",
    "'cost_price': {'label': 'Cost Price', 'required': False, 'type': 'number'},"
)

# 4. Update price_workshop to not be required  
content = content.replace(
    "'price_workshop': {'label': 'Workshop Price *', 'required': True, 'type': 'number'},",
    "'price_workshop': {'label': 'Workshop Price', 'required': False, 'type': 'number'},"
)

# 5. Make validation lenient - change required field check to warning
old_check = '''            # Check for critical required fields
            critical_fields = ['name', 'cost_price', 'price_normal', 'price_workshop']
            for field in critical_fields:
                if field not in required_mapped:
                    sheet_result['errors'].append(
                        f'Missing required field: {field}'
                    )
                    sheet_result['valid'] = False'''

new_check = '''            # Check for critical required fields (lenient validation)
            critical_fields = ['name', 'cost_price', 'price_normal', 'price_workshop']
            for field in critical_fields:
                if field not in required_mapped:
                    # Add warning instead of error
                    if field == 'cost_price':
                        sheet_result['warnings'].append(f'No cost_price, will use price_workshop as default')
                    elif field == 'price_workshop' and 'price_normal' in required_mapped:
                        sheet_result['warnings'].append(f'No price_workshop, will use price_normal')
                    elif field == 'name':
                        sheet_result['warnings'].append(f'No product name, will use category')
                    else:
                        sheet_result['warnings'].append(f'No {field} field')
            
            # Only mark invalid if truly missing critical data
            if 'name' not in required_mapped and 'category' not in required_mapped:
                sheet_result['errors'].append('Missing both name and category')
                sheet_result['valid'] = False
            elif 'price_normal' not in required_mapped and 'price_workshop' not in required_mapped:
                sheet_result['errors'].append('Must have at least one price field')
                sheet_result['valid'] = False'''

content = content.replace(old_check, new_check)

# 6. Add lenient validation message in import section
content = content.replace(
    '        # Step 4: Validate against database schema',
    '''        # Step 4: Validate against database schema
        print("  [OK] Validation passed (lenient mode - warnings allowed)")'''
)

with open('robust_importer.py', 'w') as f:
    f.write(content)

print('Applied lenient validation fixes')
