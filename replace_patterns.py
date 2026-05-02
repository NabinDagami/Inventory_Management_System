# Find and replace the patterns section
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Build new patterns
new_patterns_lines = []
new_patterns_lines.append("        # Excel column mapping patterns\n")
new_patterns_lines.append("        self.column_patterns = {\n")
new_patterns_lines.append("            'name': [\n")
new_patterns_lines.append("                r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', \n")
new_patterns_lines.append("                r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'sku': [\n")
new_patterns_lines.append("                r'^sku$', r'^code$', r'product.*code',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'category': [\n")
new_patterns_lines.append("                r'^category$', r'^type$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'brand': [\n")
new_patterns_lines.append("                r'^brand$', r'^company$', r'^manufacturer$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'stock': [\n")
new_patterns_lines.append("                r'^qty.*hand$', r'^stock$', r'^quantity$', r'^available.*stock$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'qty_sold': [\n")
new_patterns_lines.append("                r'^qty.*sold$', r'^sold$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'price_normal': [\n")
new_patterns_lines.append("                r'^retail.*', r'^price.*', r'^normal.*',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'price_workshop': [\n")
new_patterns_lines.append("                r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'cost_price': [\n")
new_patterns_lines.append("                r'^cost.*price$', r'^purchase.*price$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'reorder_level': [\n")
new_patterns_lines.append("                r'^reorder.*level$', r'^min.*stock$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'description': [\n")
new_patterns_lines.append("                r'^description$',\n")
new_patterns_lines.append("            ],\n")
new_patterns_lines.append("            'status': [\n")
new_patterns_lines.append("                r'^status$',\n")
new_patterns_lines.append("            ]\n")
new_patterns_lines.append("        }\n")

# Find the range to replace (from line 63 to end of patterns)
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if i >= 62 and 'self.column_patterns = {' in line:  # 0-indexed, line 63 is idx 62
        start_idx = i
    if start_idx is not None and end_idx is None:
        if i > start_idx and line.strip() == '}':
            # Check next line is not part of patterns
            if i+1 < len(lines) and 'self.errors' in lines[i+1]:
                end_idx = i + 1
                break

if start_idx is not None and end_idx is not None:
    # Replace
    new_lines = lines[:start_idx] + new_patterns_lines + lines[end_idx:]
    
    with open('robust_importer.py', 'w') as f:
        f.writelines(new_lines)
    
    print(f'Replaced patterns (lines {start_idx+1} to {end_idx+1})')
else:
    print(f'Could not find pattern range. start={start_idx}, end={end_idx}')
