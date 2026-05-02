# Check what sheets are in the file
import pandas as pd

xl = pd.ExcelFile('Diwan Autoparts backup.xlsx')
print(f'Total sheets: {len(xl.sheet_names)}')
print('\nAll sheets:')
for name in xl.sheet_names:
    print(f'  "{name}"')

excluded_sheets = ['Home', 'Dashboard', 'Sheet1', 'Daya form', '/', '']
print('\nChecking exclusions:')
for name in xl.sheet_names:
    skip = False
    for excluded in excluded_sheets:
        if excluded in name or name == excluded:
            skip = True
            print(f'  "{name}" -> SKIP (matches "{excluded}")')
            break
    if not skip:
        print(f'  "{name}" -> KEEP')
