import sys

# Read file
with open('robust_importer.py', 'r') as f:
    content = f.read()

# Replace Unicode checkmarks
content = content.replace('✓', '[OK]')
content = content.replace('✗', '[FAIL]')
content = content.replace('⚠', '[WARN]')
content = content.replace('⏸️', '[PAUSE]')

# Write back
with open('robust_importer.py', 'w') as f:
    f.write(content)

print('Fixed unicode characters')
