import sys

# Read file as binary
with open('robust_importer.py', 'rb') as f:
    content = f.read()

# Decode as utf-8 ignoring errors
content = content.decode('utf-8', errors='ignore')

# Replace Unicode checkmarks
content = content.replace('✓', '[OK]')
content = content.replace('✗', '[FAIL]')
content = content.replace('⚠', '[WARN]')
content = content.replace('⏸️', '[PAUSE]')

# Write back as utf-8
with open('robust_importer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed unicode characters')
