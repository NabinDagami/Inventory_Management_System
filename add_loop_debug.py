# Add debug to the loop in validate_excel_structure
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find the loop
for i, line in enumerate(lines):
    if 'for sheet_name in excel_file.sheet_names:' in line:
        # Add debug after this line
        indent = ' ' * 12
        lines.insert(i+1, f'{indent}print(f"  [VALIDATE] Processing sheet: {{sheet_name}}")\n')
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Added loop debug')