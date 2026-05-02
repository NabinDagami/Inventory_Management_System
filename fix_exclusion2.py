# Rebuild the file with correct exclusion logic
with open('robust_importer.py', 'r') as f:
    content = f.read()

# Remove the buggy exclusion check
old_exclusion = '''            for sheet_name in excel_file.sheet_names:
                if any(excluded in sheet_name for excluded in excluded_sheets):
                    continue'''

new_exclusion = '''            for sheet_name in excel_file.sheet_names:
                # Skip excluded sheets (exact match or non-empty substring)
                skip = False
                for excluded in excluded_sheets:
                    if excluded and excluded in sheet_name:
                        skip = True
                        break
                if skip:
                    continue'''

if old_exclusion in content:
    content = content.replace(old_exclusion, new_exclusion)
    with open('robust_importer.py', 'w') as f:
        f.write(content)
    print('Fixed exclusion logic')
else:
    print('Old exclusion not found as-is')
