# Fix the orphaned lines
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Remove orphaned lines after 'pass  # Allow sheets with missing fields'
new_lines = []
i = 0
while i < len(lines):
    if 'pass  # Allow sheets with missing fields' in lines[i]:
        new_lines.append(lines[i])
        i += 1
        # Skip orphaned lines with incorrect indentation
        while i < len(lines) and (lines[i].strip().startswith('sheet_result[\'errors\'].append') or 
                                  lines[i].strip().startswith('sheet_result[\'valid\'] = False') or
                                  lines[i].strip().startswith('Must have') or
                                  lines[i].strip().startswith('Missing both')):
            print(f'Skipping orphaned line: {lines[i].rstrip()}')
            i += 1
        continue
    elif 'pass  # Allow import even with some field issues' in lines[i]:
        new_lines.append(lines[i])
        i += 1
        # Skip orphaned valid = False line
        while i < len(lines) and lines[i].strip().startswith('sheet_result[\'valid\'] = False'):
            print(f'Skipping orphaned line: {lines[i].rstrip()}')
            i += 1
        continue
    else:
        new_lines.append(lines[i])
        i += 1

with open('robust_importer.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed orphaned lines')