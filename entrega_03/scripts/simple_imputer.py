import pandas as pd
from sklearn.impute import SimpleImputer

DATA_FILE = "dataset/final.csv"
OUTPUT_FILE = "dataset/final_imputed.csv"

# Columns to impute
NUMERIC_COLS = [
    "bathrooms", "beds", "bedrooms", "host_total_listings_count", "reviews_per_month"
] + [c for c in pd.read_csv(DATA_FILE, nrows=0).columns if c.startswith("review_scores_")]

def main():
    df = pd.read_csv(DATA_FILE)

    for col in NUMERIC_COLS:
        if df[col].isnull().sum() > 0:
            # Ensure numeric type
            df[col] = pd.to_numeric(df[col], errors='coerce')
            median_value = df[col].median()
            df[col].fillna(median_value, inplace=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved imputed CSV as {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

