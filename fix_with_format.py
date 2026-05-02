# Use .format instead
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and replace the broken section
new_lines = []
skip_next = 0
for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue
    
    if 'Sheet details count' in line:
        # Replace this line and the next 4
        indent = ' ' * 8
        new_lines.append(f'{indent}print("  Sheet details count: {{}}".format(len(validation["sheet_details"])))\n')
        new_lines.append(f'{indent}for s in validation["sheet_details"][:3]:\n')
        new_lines.append(f'{indent}    print("    {{}}: valid={{}}, mappings={{}}".format(s["sheet_name"], s["valid"], len(s.get("column_mapping", {{}}))))\n')
        new_lines.append(f'{indent}    if s.get("column_mapping"):\n')
        new_lines.append(f'{indent}        print("      Mappings: {{}}".format(s["column_mapping"]))\n')
        skip_next = 4  # Skip the next 4 lines we replaced
        continue
    
    new_lines.append(line)

with open('robust_importer.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed with .format')