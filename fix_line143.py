# Replace line 143
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

lines[142] = '                    print(f"  MAPPED {sheet_name}: {sheet_result[\'column_mapping\']}")\n'

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Replaced line 143')