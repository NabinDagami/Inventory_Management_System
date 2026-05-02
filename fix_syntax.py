import codecs

# Read file
with codecs.open('src/utils/excel_mapper.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 1853-1854
# Line 1853 (index 1852) has: '                            available_stock\r\n'
# Line 1854 (index 1853) has: '                        imported_count += 1\r\n'
# Need to change to:
# '                            available_stock\r\n'
# '                        ))\r\n'
# '                        \r\n'
# '                        imported_count += 1\r\n'

if len(lines) > 1853:
    # Fix line 1853 (0-indexed 1852)
    lines[1852] = '                            available_stock\r\n'
    # Add closing paren and blank line
    lines.insert(1853, '                        ))\r\n')
    lines.insert(1854, '\r\n')
    # Keep imported_count line (it's now at line 1855)
    
    # Write back
    with codecs.open('src/utils/excel_mapper.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print('Fixed excel_mapper.py syntax error')
else:
    print('File too short')
