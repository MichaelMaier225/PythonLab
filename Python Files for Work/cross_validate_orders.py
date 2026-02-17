import os
import pandas as pd
import warnings

# Optional: suppress pandas dtype warnings
warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)

# Set your folder path
folder_path = r"C:\Users\Micha\OneDrive\Desktop\Work Project Folder\Queens of Sparkles\Excel Organize"

# Cleaning function
def clean(x):
    return str(x).strip().lower()

# Step 1: Load and clean wholesale orders
all_order_names = []

for i in range(1, 6):
    file_path = os.path.join(folder_path, f"orders_export_{i}.csv")
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    
    name_col = [col for col in df.columns if "name" in col]
    if not name_col:
        print(f"❌ orders_export_{i}.csv has no 'Name' column.")
        continue

    cleaned_names = df[name_col[0]].dropna().astype(str).map(clean).tolist()
    all_order_names.extend(cleaned_names)

unique_wholesale_ids = set(all_order_names)

# Step 2: Load and clean 3_Months_of_Fees.csv
fees_file = os.path.join(folder_path, "3_Months_of_Fees.csv")
fees_df = pd.read_csv(fees_file, encoding="utf-8-sig")
fees_df.columns = fees_df.columns.str.strip().str.lower()

order_col = [col for col in fees_df.columns if "order" in col]
if not order_col:
    raise Exception("❌ No 'Order' column found in 3_Months_of_Fees.csv.")

fees_orders = fees_df[order_col[0]].dropna().astype(str).map(clean).tolist()
unique_payment_ids = set(fees_orders)

# Step 3: Get matched wholesale orders with payments
matched_wholesale_ids = unique_wholesale_ids & unique_payment_ids

print(f"✅ Total wholesale orders with payment: {len(matched_wholesale_ids)}")

# Step 4: Save the result
output_dir = os.path.join(folder_path, "comparison_results")
os.makedirs(output_dir, exist_ok=True)

pd.DataFrame(sorted(matched_wholesale_ids), columns=["Wholesale Order IDs With Payment"]).to_csv(
    os.path.join(output_dir, "matched_wholesale_orders.csv"),
    index=False
)

print("📁 Saved matched wholesale orders with payments to 'comparison_results/matched_wholesale_orders.csv'")
