# Fix the duplicated method definition
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find and fix the duplicates
new_lines = []
i = 0
while i < len(lines):
    if i < len(lines) - 1 and 'def _validate_sheet' in lines[i] and 'def _validate_sheet' in lines[i+1]:
        # Keep the second one (which has the proper indentation after it)
        # Actually, both are identical, so just keep one
        new_lines.append(lines[i])
        i += 2  # Skip the duplicate
    else:
        new_lines.append(lines[i])
        i += 1

with open('robust_importer.py', 'w') as f:
    f.writelines(new_lines)

print('Removed duplicate method definition')