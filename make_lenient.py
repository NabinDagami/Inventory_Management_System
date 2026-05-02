# Update the robust importer to use lenient validation
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Build new version with fixes
# 1. Update column_patterns to not map 'status' and prioritize name > brand
# 2. Update validation to be lenient (warnings not errors)
# 3. Update cost_price handling

new_file = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Update patterns - remove status, fix priority
    if "'status': [" in line and i > 100 and "COLUMN_SUGGESTIONS" not in lines[i-5]:
        # Skip status pattern (we're in column_patterns)
        # Just don't add it to new_file
        i += 1
        continue
    
    # Update the validation logic to be lenient
    if "# Check for critical required fields" in line:
        # Replace from this line until after the critical_fields check
        new_file.append(line)
        i += 1
        # Skip old critical field checking (lines 221-228)
        # Replace with lenient checking
        new_file.append("            # Check for critical required fields (lenient - warn but don't fail)\n")
        new_file.append("            critical_fields = ['name', 'cost_price', 'price_normal', 'price_workshop']\n")
        new_file.append("            for field in critical_fields:\n")
        new_file.append("                if field not in required_mapped:\n")
        new_file.append("                    # Add as warning, not error - we can derive or default\n")
        new_file.append("                    if field == 'cost_price':\n")
        new_file.append("                        sheet_result['warnings'].append(f'Missing cost_price, will use price_workshop as default')\n")
        new_file.append("                    elif field == 'price_workshop' and 'price_normal' in required_mapped:\n")
        new_file.append("                        sheet_result['warnings'].append(f'Missing price_workshop, will use price_normal')\n")
        new_file.append("                    elif field == 'name':\n")
        new_file.append("                        sheet_result['warnings'].append(f'Missing product name, using category as fallback')\n")
        new_file.append("                    else:\n")
        new_file.append("                        sheet_result['warnings'].append(f'Missing required field: {field}')\n")
        new_file.append("            \n")
        
        # Skip old lines
        while i < len(lines) and ('sheet_result[\'valid\'] = False' not in lines[i] or 'critical_fields' not in lines[i-3]):
            if "# Validate data types and integrity" in lines[i]:
                break
            i += 1
        continue
    
    new_file.append(line)
    i += 1

with open('robust_importer_limited.py', 'w') as f:
    f.writelines(new_file)

print('Created lenient version')
