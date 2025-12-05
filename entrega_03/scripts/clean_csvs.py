#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = "dataset"
OUTPUT_FILE = "dataset/final.csv"
column_summary = True

# Only keep these columns
COLUMNS = [
    "description", "host_since", "host_location", "host_response_time",
    "host_response_rate", "host_acceptance_rate", "host_is_superhost",
    "host_total_listings_count", "host_has_profile_pic", "host_identity_verified",
    "neighbourhood_group_cleansed", "latitude", "longitude", "property_type", "accommodates",
    "bathrooms", "bedrooms", "beds", "amenities", "price", "number_of_reviews",
    "number_of_reviews_l30d", "availability_eoy", "instant_bookable", "review_scores_rating",
    "review_scores_accuracy", "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location", "review_scores_value", "reviews_per_month"
]

# Boolean-like columns
BOOL_COLS = ["host_is_superhost", "host_has_profile_pic", "host_identity_verified", "instant_bookable"]

# Numeric columns
NUMERIC_COLS = [
    "latitude", "longitude", "accommodates", "bathrooms", "bedrooms", "beds",
    "price", "number_of_reviews", "number_of_reviews_l30d", "availability_eoy",
    "review_scores_rating", "review_scores_accuracy", "review_scores_cleanliness",
    "review_scores_checkin", "review_scores_communication", "review_scores_location",
    "review_scores_value", "reviews_per_month"
]

def clean_text(df):
    """Clean string columns."""
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.replace("\r", " ").str.strip()
    return df

def purify_df(df):
    """Convert disguised nulls to proper NaN and enforce types."""
    # Replace common placeholders with NaN
    df.replace({"": np.nan, "nan": np.nan, "NaN": np.nan}, inplace=True)

    # Convert boolean-like columns
    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].map({"t": True, "f": False, np.nan: np.nan})

    # Convert numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            if col == "price":
                df[col] = df[col].astype(str).str.replace(r"[\$,]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# luego borrar
def baseline_impute(df):
    """Simple baseline imputation."""
    for col in df.columns:
        if col in NUMERIC_COLS:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
        elif col in BOOL_COLS:
            mode_val = df[col].mode(dropna=True)
            if not mode_val.empty:
                df[col].fillna(mode_val[0], inplace=True)
        else:
            # Treat as categorical/text
            mode_val = df[col].mode(dropna=True)
            if not mode_val.empty:
                df[col].fillna(mode_val[0], inplace=True)
    return df


def main():
    frames = []

    for city_folder in Path(DATA_DIR).iterdir():
        if not city_folder.is_dir():
            continue

        csv_file = city_folder / "listings.csv"
        if not csv_file.exists():
            continue

        print(f"Loading {csv_file} ...")
        df = pd.read_csv(csv_file, low_memory=False)

        # Keep only the columns we care about
        keep = [c for c in COLUMNS if c in df.columns]
        df = df[keep]

        df = clean_text(df)
        df = purify_df(df)

        df["city"] = city_folder.name
        frames.append(df)

    if not frames:
        print("No data found. Exiting.")
        return

    final = pd.concat(frames, ignore_index=True)
    # esto es provisional
    final = baseline_impute(final)
    final.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved purified CSV as {OUTPUT_FILE}")

    if column_summary:
        print("\nColumn Summary:")
        for col in final.columns:
            null_pct = final[col].isnull().mean() * 100
            try:
                col_min = final[col].min()
                col_max = final[col].max()
            except TypeError:
                col_min = col_max = "N/A"
            print(f"{col}: nulls={null_pct:.2f}%, min={col_min}, max={col_max}")

if __name__ == "__main__":
    main()

