import pandas as pd
import json
import os

# Read the Excel file
file_path = 'Diwan Autoparts backup.xlsx'
df_dict = pd.read_excel(file_path, sheet_name=None)

# Create output directory
output_dir = 'extracted_data'
os.makedirs(output_dir, exist_ok=True)

# Extract data from each sheet
all_data = {}

for sheet_name, df in df_dict.items():
    # Clean column names - remove 'Unnamed:' columns and NaN columns
    columns = [col for col in df.columns if pd.notna(col) and 'Unnamed:' not in str(col)]
    
    # If no valid columns, skip
    if not columns:
        continue
    
    # Filter dataframe to only valid columns
    df_clean = df[columns].copy()
    
    # Remove rows where all values are NaN
    df_clean = df_clean.dropna(how='all')
    
    # Convert to dictionary
    sheet_data = df_clean.to_dict('records')
    
    # Clean up the records - remove NaN values
    cleaned_records = []
    for record in sheet_data:
        cleaned_record = {k: (v if pd.notna(v) else None) for k, v in record.items()}
        # Only add if there's at least one non-None value
        if any(v is not None for v in cleaned_record.values()):
            cleaned_records.append(cleaned_record)
    
    if cleaned_records:
        all_data[sheet_name] = cleaned_records

# Save to JSON file
output_file = os.path.join(output_dir, 'diwan_autoparts_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"Data extracted to: {output_file}")
print(f"Total sheets processed: {len(all_data)}")
print(f"\nSheets extracted:")
for sheet_name, records in all_data.items():
    print(f"  - {sheet_name}: {len(records)} records")