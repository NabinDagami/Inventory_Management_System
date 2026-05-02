# Add debug right after field_errors is computed
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'field_errors = self._validate_data_integrity' in line:
        indent = ' ' * 12
        # Insert after the next line (which extends errors)
        for j in range(i+1, min(i+5, len(lines))):
            if 'sheet_result[\'errors\'].extend(field_errors)' in lines[j]:
                lines.insert(j+1, f'{indent}print(f"    field_errors for {sheet_name}: {{field_errors}}")\n')
                break
        break

with open('robust_importer.py', 'w') as f:
    f.writelines(lines)

print('Added field_errors debug')