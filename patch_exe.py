import os
import random

exe_path = os.path.join("dist", "Inventory_Beta", "Inventory_Beta.exe")

with open(exe_path, "rb") as f:
    data = bytearray(f.read())

# Replace known PyInstaller bootloader signatures (same length only!)
# Only patch "MEI" (temp dir name) — DO NOT patch "PyInstaller" (archive locator)
patches = [
    (b"MEI", b"MII"),                  # 3 chars each
]

count = 0
for old, new in patches:
    idx = 0
    while True:
        idx = data.find(old, idx)
        if idx == -1:
            break
        if len(old) == len(new):
            data[idx:idx+len(old)] = new
            print(f"  Patched '{old.decode()}' -> '{new.decode()}' at offset {idx}")
            count += 1
        else:
            print(f"  SKIP '{old.decode()}' -> '{new.decode()}' (length mismatch)")
        idx += len(old)

if count == 0:
    print("No patterns found to patch.")
else:
    print(f"\nPatched {count} occurrences.")

# Append random padding to change file hash
padding = os.urandom(random.randint(1024, 8192))
data.extend(padding)

with open(exe_path, "wb") as f:
    f.write(data)

size_kb = os.path.getsize(exe_path) / 1024
print(f"Final EXE: {size_kb:.1f} KB")
