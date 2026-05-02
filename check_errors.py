# Check errors list
with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

for i in range(245, 275):
    print(f'{i+1}: {lines[i]}', end='')