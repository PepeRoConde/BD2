#!/usr/bin/env python3
import pandas as pd
from pymongo import MongoClient
import ast  # to safely parse amenities list

DATA_FILE = "dataset/final_imputed.csv"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"

# Define columns for embedded documents
HOST_COLS = [
    "host_since", "host_location", "host_response_time",
    "host_response_rate", "host_acceptance_rate", "host_is_superhost",
    "host_total_listings_count", "host_has_profile_pic", "host_identity_verified"
]

SCORE_COLS = [
    "review_scores_rating", "review_scores_accuracy", "review_scores_cleanliness",
    "review_scores_checkin", "review_scores_communication", "review_scores_location",
    "review_scores_value"
]

# Remaining columns for top-level attributes
TOP_LEVEL_COLS = [
    "description","neighbourhood","latitude","longitude","property_type",
    "accommodates","bathrooms","bedrooms","beds","price","number_of_reviews",
    "number_of_reviews_l30d","availability_eoy","instant_bookable","reviews_per_month","city"
]

def parse_amenities(amenities_str):
    """Convert amenities string into a list."""
    if pd.isnull(amenities_str):
        return []
    try:
        # CSV often stores amenities like a string list: "{Amenity1, Amenity2}"
        amenities = amenities_str.strip("{}").split(",")
        return [a.strip().strip('"') for a in amenities if a.strip()]
    except Exception:
        return []

def main():
    df = pd.read_csv(DATA_FILE)
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    documents = []
    for _, row in df.iterrows():
        doc = {col: row[col] for col in TOP_LEVEL_COLS}
        doc["host"] = {col: row[col] for col in HOST_COLS}
        doc["score"] = {col: row[col] for col in SCORE_COLS}
        doc["amenities"] = parse_amenities(row["amenities"])
        documents.append(doc)

    # Insert into MongoDB
    if documents:
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} listings into {DB_NAME}.{COLLECTION_NAME}")

if __name__ == "__main__":
    main()

