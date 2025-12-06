#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import numpy as np
import argparse
import sys

KEEP = [
    "description", "host_since", "host_location", "host_response_time",
    "host_response_rate", "host_acceptance_rate", "host_is_superhost",
    "host_total_listings_count", "host_has_profile_pic", "host_identity_verified",
    "neighbourhood_group_cleansed", "latitude", "longitude", "property_type", 
    "accommodates", "bathrooms", "bedrooms", "beds", "amenities", "price", 
    "number_of_reviews", "number_of_reviews_l30d", "availability_eoy", 
    "instant_bookable", "review_scores_rating", "review_scores_accuracy", 
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location", 
    "review_scores_value", "reviews_per_month"
]

BOOL_COLS = [
    "host_is_superhost", 
    "host_has_profile_pic", 
    "host_identity_verified", 
    "instant_bookable"
]

NUM_COLS = [
    "latitude", "longitude", "accommodates", "bathrooms", "bedrooms", "beds",
    "price", "number_of_reviews", "number_of_reviews_l30d", "availability_eoy",
    "review_scores_rating", "review_scores_accuracy", "review_scores_cleanliness",
    "review_scores_checkin", "review_scores_communication", "review_scores_location",
    "review_scores_value", "reviews_per_month"
]


def fix_text(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.replace("\r", " ").str.strip()
    return df


def fix_types(df):
    df.replace(["", "nan", "NaN", "null", "NULL", "NA", "N/A"], np.nan, inplace=True)
    
    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].map({
                "t": True, 
                "f": False,
                "True": True,
                "False": False,
                "true": True,
                "false": False
            })
    
    for col in NUM_COLS:
        if col in df.columns:
            if col == "price":
                df[col] = df[col].astype(str).str.replace(r"[\$,]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df


def fill_na(df):
    print("Filling gaps...")
    for col in df.columns:
        # se non ten nulos non fas nada
        if df[col].isnull().sum() == 0:
            continue
        # se é numerica usas a mediana
        if col in NUM_COLS:
            df[col].fillna(df[col].median(), inplace=True)
        # se é bool usas a moda (se podes)
        elif col in BOOL_COLS:
            modes = df[col].mode(dropna=True)
            if not modes.empty:
                df[col].fillna(modes.iloc[0], inplace=True)
        # e un fallback ca moda tamén
        else:
            modes = df[col].mode(dropna=True)
            if not modes.empty:
                df[col].fillna(modes.iloc[0], inplace=True)
    return df


def show_stats(df):
    print("\n" + "-"*60)
    print("COLUMN STATS")
    print("-"*60)
    for col in df.columns:
        nulls = df[col].isnull().sum()
        total = len(df)
        null_pct = (nulls / total) * 100
        try:
            low = df[col].min()
            high = df[col].max()
            range_str = f"{low} to {high}"
        except:
            uniq = df[col].nunique()
            range_str = f"{uniq} unique"
        print(f"{col}: {nulls:,} missing ({null_pct:.1f}%), range: {range_str}")
    print("-"*60)
    print(f"Total: {len(df):,} rows, {len(df.columns)} cols")
    print("-"*60)


def get_args():
    parser = argparse.ArgumentParser(description="Merge city Airbnb data")
    parser.add_argument("--input", "-i", default="dataset", help="folder with city subfolders")
    parser.add_argument("--output", "-o", default="dataset/merged.csv", help="where to save")
    parser.add_argument("--impute", action="store_true", default=True, help="fill missing (default)")
    parser.add_argument("--no-impute", dest="impute", action="store_false", help="skip filling")
    parser.add_argument("--summary", action="store_true", default=True, help="show stats")
    parser.add_argument("--no-summary", dest="summary", action="store_false", help="no stats")
    parser.add_argument("--summary-only", action="store_true", help="just stats, no save")
    return parser.parse_args()


def main():
    args = get_args()
    in_dir = Path(args.input)
    out_file = Path(args.output)
    
    if not in_dir.exists():
        print(f"Can't find {in_dir}!")
        sys.exit(1)
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading from: {in_dir}")
    print(f"Saving to: {out_file}")
    print(f"Impute: {'yes' if args.impute else 'no'}")
    print(f"Summary: {'yes' if args.summary else 'no'}")
    print("-" * 40)
    
    all_data = []
    cities_done = 0
    
    for city_folder in in_dir.iterdir():
        if not city_folder.is_dir():
            continue
        
        data_file = city_folder / "listings.csv"
        if not data_file.exists():
            continue
        
        print(f"Loading {city_folder.name}...", end=" ")
        try:
            city_df = pd.read_csv(data_file, low_memory=False)
            keep_cols = [c for c in KEEP if c in city_df.columns]
            city_df = city_df[keep_cols]
            city_df = fix_text(city_df)
            city_df = fix_types(city_df)
            city_df["city"] = city_folder.name
            all_data.append(city_df)
            cities_done += 1
            print(f"ok ({len(city_df):,} rows)")
        except Exception as e:
            print(f"failed: {e}")
            continue
    
    if cities_done == 0:
        print("Nothing loaded!")
        sys.exit(1)
    
    print(f"\nGot data from {cities_done} cities")
    merged = pd.concat(all_data, ignore_index=True)
    print(f"Merged: {len(merged):,} rows, {len(merged.columns)} cols")
    
    if args.impute:
        merged = fill_na(merged)
    
    if args.summary:
        show_stats(merged)
    
    if not args.summary_only:
        print(f"\nWriting {out_file}...")
        merged.to_csv(out_file, index=False)
        print("Done!")
    
    print(f"\nFinal shape: {merged.shape}")
    print(f"Memory: {merged.memory_usage(deep=True).sum() / 1024**2:.1f} MB")


if __name__ == "__main__":
    main()
