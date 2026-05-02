with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Validation failed with' in line:
        print(f'{i+1}: {line.rstrip()}')
        print(f'{i+2}: {lines[i+1].rstrip() if i+1 < len(lines) else "EOF"}')
        print(f'{i+3}: {lines[i+2].rstrip() if i+2 < len(lines) else "EOF"}')
        # Print 10 lines before
        print('\nBefore:')
        for j in range(max(0, i-10), i):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
