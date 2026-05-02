# Find where "Validation failed" is printed
with open('robust_importer.py', 'r') as f:
    content = f.read()

import re
matches = list(re.finditer('Validation failed', content))
for m in matches:
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 50)
    print(f'Found at position {m.start()}:')
    print(f'  {content[start:end]}')
    print()