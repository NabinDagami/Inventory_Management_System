# Fix all orphaned lines after pass statements
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Check if this line is a pass with comment about allowing import
    if 'pass  # Allow' in line or line.strip() == 'pass':
        i += 1
        # Skip any lines that look like they belong to old validation
        while i < len(lines):
            next_line = lines[i]
            stripped = next_line.strip()
            # Check for orphaned validation lines
            if ("sheet_result['valid'] = False" in next_line and 
                next_line.startswith(' ' * 16)) or \
               ("sheet_result['errors'].append(" in next_line and 
                next_line.startswith(' ' * 16)):
                print(f'Skipping orphaned: {next_line.rstrip()}')
                i += 1
            else:
                break
        continue
    
    i += 1

with open('robust_importer.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed all orphaned lines')