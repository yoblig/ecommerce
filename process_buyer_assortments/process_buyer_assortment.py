import pandas as pd
import glob
import os

# Auto-detect Excel file
xlsx_files = [f for f in glob.glob("*.xlsx") if not os.path.basename(f).startswith("~$")]
if not xlsx_files:
    raise FileNotFoundError("No .xlsx file found in the current directory.")

file_path = xlsx_files[0]
print(f"Processing file: {file_path}")

# Generate output CSV filename
base_name = os.path.splitext(os.path.basename(file_path))[0]
output_csv = f"{base_name}.csv"

# Load raw Excel to find header row
df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
keywords = ['BOOKSTORE DESCRIPTION', 'NETSUITE DESCRIPTION', 'VENDOR STYLE #']
header_row = next(
    (i for i, row in df_raw.iterrows() if any(k in str(cell) for cell in row for k in keywords)),
    None
)

if header_row is not None:
    df = pd.read_excel(file_path, skiprows=header_row, engine='openpyxl')

    # Find relevant columns
    desc_col = next((c for c in df.columns if c in ['BOOKSTORE DESCRIPTION', 'NETSUITE DESCRIPTION', 'DESCRIPTION']), None)
    style_col = next((c for c in df.columns if 'VENDOR STYLE #' in str(c)), None)
    if desc_col:
        cols = [desc_col] + ([style_col] if style_col else [])
        cleaned = df[cols].dropna(how='all').copy()
        col_names = ['ITEM_NAME'] + (['VENDOR_STYLE'] if style_col else [])
        cleaned.columns = col_names
        cleaned = cleaned.dropna(subset=['ITEM_NAME']).reset_index(drop=True)
        if style_col:
            cleaned['VENDOR_STYLE'] = cleaned['VENDOR_STYLE'].astype(str).str.strip()
        cleaned.to_csv(output_csv, index=False)
        print(f"✅ Saved cleaned data to: {output_csv}")
    else:
        print("❌ Description column not found.")
else:
    print("❌ Header row not found.")