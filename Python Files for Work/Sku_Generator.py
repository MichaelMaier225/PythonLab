import pandas as pd
import os

# Function to build SKU from all non-empty fields
def generate_sku(row):
    parts = ['QOS']
    handle = str(row[0]).strip()
    val_j = str(row[9]).strip()
    val_m = str(row[12]).strip()
    color = str(row[15]).strip() if len(row) > 15 else ''

    for val in [handle, val_j, val_m, color]:
        if val and val.upper() != 'UNKNOWN':
            parts.append(val)

    if len(parts) < 3:
        return ''  # skip rows with not enough info

    return '-'.join(parts)

# Path to the CSV
base_path = r"C:\Users\Micha\OneDrive\Desktop\Work Project Folder\Queens of Sparkles\SKU_Generator"
input_file = os.path.join(base_path, "combined_export_1.csv")
output_file = os.path.join(base_path, "Final_SKU_Output.csv")

# Load CSV
print(f"📥 Loading file: {input_file}")
df = pd.read_csv(input_file)

# Make sure there's room for SKU in column R (index 17)
while len(df.columns) <= 17:
    df[f'Extra_Col_{len(df.columns)}'] = ''

# Generate SKU
df.iloc[:, 17] = df.apply(generate_sku, axis=1)
df.columns.values[17] = 'SKU'

# Remove blank SKUs
df = df[df['SKU'] != '']

# Save output
df.to_csv(output_file, index=False)
print(f"✅ Done! SKU file saved at:\n{output_file}")
