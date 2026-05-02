# Check the actual code
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Find the _map_columns method
for i, line in enumerate(lines):
    if 'def _map_columns' in line:
        print(f'Found _map_columns at line {i+1}')
        # Print next 20 lines
        for j in range(i, min(i+25, len(lines))):
            print(f'{j+1}: {lines[j]}', end='')
        break
