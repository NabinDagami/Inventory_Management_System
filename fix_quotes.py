# Fix with simpler approach
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and replace the problematic line
for i, line in enumerate(lines):
    if 'MAPPED' in line and 'column_mapping' in line:
        lines[i] = '                    print(f"  MAPPED {sheet_name}: {sheet_result[\'column_mapping\']}")\n'
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Fixed with single quotes')