# Add debug to show field_errors
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find where field_errors is added
for i, line in enumerate(lines):
    if 'field_errors = self._validate_data_integrity' in line:
        # Add debug after this
        indent = ' ' * 12
        lines.insert(i+1, f'{indent}print(f"  [DEBUG] Field errors for {{sheet_name}}: {{field_errors}}\n")\n')
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Added field_errors debug')