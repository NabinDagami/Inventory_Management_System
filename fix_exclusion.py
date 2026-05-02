# Fix the exclusion logic
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and fix the exclusion logic
for i, line in enumerate(lines):
    if 'if any(excluded in sheet_name for excluded in excluded_sheets):' in line:
        # Replace with correct logic
        indent = ' ' * 16
        lines[i] = f'{indent}# Skip excluded sheets (exact match or non-empty substring)\n'
        lines.insert(i+1, f'{indent}skip = False\n')
        lines.insert(i+2, f'{indent}for excluded in excluded_sheets:\n')
        lines.insert(i+3, f'{indent}    if excluded and excluded in sheet_name:\n')
        lines.insert(i+4, f'{indent}        skip = True\n')
        lines.insert(i+5, f'{indent}        break\n')
        lines.insert(i+6, f'{indent}if skip:\n')
        lines.insert(i+7, f'{indent}    continue\n')
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Fixed exclusion logic')