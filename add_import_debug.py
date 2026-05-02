# Add debug at the start of import
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find import section
for i, line in enumerate(lines):
    if '# Step 5: Import data' in line:
        indent = ' ' * 8
        lines.insert(i+1, f'{indent}print("  [INFO] Starting actual import...\\n")\n')
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Added import debug')