# Find the line that checks sheet_result['valid']
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Look for where result['valid'] = False is set within the loop
for i, line in enumerate(lines):
    if 'result[\'valid\'] = False' in line:
        # Print context
        for j in range(max(0, i-10), min(len(lines), i+5)):
            print(f'{j+1}: {lines[j]}', end='')
        print()
