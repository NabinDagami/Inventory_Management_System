import pandas as pd

df = pd.read_excel('Diwan Autoparts backup.xlsx', sheet_name=None)
sheets = list(df.keys())
print('Sheets:', sheets)

for sheet in sheets:
    print(f'\n--- {sheet} ---')
    print(f'Shape: {df[sheet].shape}')
    print(df[sheet].head(10).to_string())
