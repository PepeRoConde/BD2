#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

DATA_DIR = "dataset"
OUTPUT_FILE = "dataset/final.csv"
column_summary = True

# Only keep these columns
COLUMNS = [
    "description", "host_since", "host_location", "host_response_time",
    "host_response_rate", "host_acceptance_rate", "host_is_superhost",
    "host_total_listings_count", "host_has_profile_pic", "host_identity_verified",
    "neighbourhood", "latitude", "longitude", "property_type", "accommodates",
    "bathrooms", "bedrooms", "beds", "amenities", "price", "number_of_reviews",
    "number_of_reviews_l30d", "availability_eoy", "review_scores_rating",
    "review_scores_accuracy", "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location", "review_scores_value",
    "instant_bookable", "reviews_per_month"
]

def clean_text(df):
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.replace("\r", " ").str.strip()
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
        df["city"] = city_folder.name

        frames.append(df)

    if not frames:
        print("No data found. Exiting.")
        return

    final = pd.concat(frames, ignore_index=True)
    final.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved merged CSV as {OUTPUT_FILE}")

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
