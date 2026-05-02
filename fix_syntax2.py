# Fix it properly
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and fix the broken line
for i, line in enumerate(lines):
    if 'Sheet details count' in line:
        # Replace with correct syntax
        indent = ' ' * 8
        lines[i] = f'{indent}print(f"  Sheet details count: {{len(validation[\"sheet_details\"])")}\n'
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Fixed syntax error')