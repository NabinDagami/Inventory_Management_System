with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
print(f'Line 143 content: {repr(lines[142] if len(lines) > 142 else "NO LINE 143")}')

# Try writing a completely new file
with open('robust_importer_new.py', 'w') as f:
    for i, line in enumerate(lines):
        if i == 142:
            f.write('                    print(f"  MAPPED {sheet_name}: {sheet_result[\'column_mapping\']}")\n')
        else:
            f.write(line)

print('Created backup')

# Verify
with open('robust_importer_new.py') as f:
    new_lines = f.readlines()
    print(f'New line 143: {repr(new_lines[142])}')
