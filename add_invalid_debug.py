# Add debug for invalid sheets
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find where result['valid'] = False is set for sheets
for i, line in enumerate(lines):
    if i >= 150 and i <= 160 and 'result[\'valid\'] = False' in line:
        # Insert debug before this line
        indent = ' ' * 16
        lines.insert(i, f'{indent}print(f"    [INVALID] {sheet_name}: {{sheet_result[\"errors\"]}}")\n')
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Added invalid sheet debug')