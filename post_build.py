import os
import random
import struct

exe_path = os.path.join("dist", "Inventory_Beta", "Inventory_Beta.exe")

if not os.path.exists(exe_path):
    print(f"EXE not found at {exe_path}")
    exit(1)

with open(exe_path, "ab") as f:
    padding = os.urandom(random.randint(512, 4096))
    f.write(padding)

size_kb = os.path.getsize(exe_path) / 1024
print(f"Padded EXE: {size_kb:.1f} KB")
