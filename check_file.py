# Check file size and modification time
import os
import time

stat = os.stat('robust_importer.py')
print(f'File size: {stat.st_size} bytes')
print(f'Modified: {time.ctime(stat.st_mtime)}')

# Read last 20 lines
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()
    
print(f'\nTotal lines: {len(lines)}')
print('\nLast 20 lines:')
for i, line in enumerate(lines[-20:], len(lines)-19):
    print(f'{i:4d}: {line.rstrip()[-80:]}')

# Check if the line from add_debug7 is there
print('\nSearching for debug additions:')
for keyword in ['Sheet details count', 'for s in validation', 's\["sheet_name"\]']:
    found = any(keyword in line for line in lines)
    print(f'  {keyword}: {found}')