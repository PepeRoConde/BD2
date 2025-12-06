#!/usr/bin/env python3
import pandas as pd
from pymongo import MongoClient
import ast  # to safely parse amenities list

DATA_FILE = "dataset/merged.csv"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"

# Define columns for embedded documents (without prefixes)
HOST_COLS = [
    ("host_since", "since"),
    ("host_location", "location"),
    ("host_response_time", "response_time"),
    ("host_response_rate", "response_rate"),
    ("host_acceptance_rate", "acceptance_rate"),
    ("host_is_superhost", "is_superhost"),
    ("host_total_listings_count", "total_listings_count"),
    ("host_has_profile_pic", "has_profile_pic"),
    ("host_identity_verified", "identity_verified")
]

SCORE_COLS = [
    ("review_scores_rating", "rating"),
    ("review_scores_accuracy", "accuracy"),
    ("review_scores_cleanliness", "cleanliness"),
    ("review_scores_checkin", "checkin"),
    ("review_scores_communication", "communication"),
    ("review_scores_location", "location"),
    ("review_scores_value", "value")
]

# Remaining columns for top-level attributes
TOP_LEVEL_COLS = [
    "description","neighbourhood_group_cleansed","latitude","longitude","property_type",
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
    for i, row in df.iterrows():
        # Top level columns
        doc = {col: row[col] for col in TOP_LEVEL_COLS}
        
        # Host embedded document (without "host_" prefix)
        doc["host"] = {new_col: row[old_col] for old_col, new_col in HOST_COLS}
        
        # Score embedded document (without "review_scores_" prefix)
        doc["score"] = {new_col: row[old_col] for old_col, new_col in SCORE_COLS}
        
        # Amenities list
        doc["amenities"] = parse_amenities(row["amenities"])
        
        doc["row_id"] = i

        documents.append(doc)

    # Insert into MongoDB
    if documents:
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} listings into {DB_NAME}.{COLLECTION_NAME}")

if __name__ == "__main__":
    main()
