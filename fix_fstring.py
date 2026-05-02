# Fix the syntax error in validate_excel_structure
with open('robust_importer.py', 'r') as f:
    content = f.read()

# Fix the f-string quote issue
old_line = '                    print(f"  MAPPED {sheet_name}: {sheet_result["column_mapping"]}")\n'
new_line = '                    print(f"  MAPPED {sheet_name}: {{sheet_result[\"column_mapping\"]}}")\n'

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('robust_importer.py', 'w') as f:
        f.write(content)
    print('Fixed f-string syntax error')
else:
    print('Line not found, trying alternative...')
    # Try with different spacing
    import re
    content = re.sub(
        r'print\(f"  MAPPED \{sheet_name\}: \{sheet_result\["column_mapping"\]\}"\)',
        'print(f"  MAPPED {sheet_name}: {sheet_result[\\"column_mapping\\"]}")',
        content
    )
    with open('robust_importer.py', 'w') as f:
        f.write(content)
    print('Fixed with regex')
