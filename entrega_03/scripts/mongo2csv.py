#!/usr/bin/env python3
import pandas as pd
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"
OUTPUT_FILE = "dataset/final_with_centrality.csv"

def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch all documents
    cursor = collection.find().sort("row_id", 1)
    df = pd.DataFrame(list(cursor))

    if df.empty:
        print("No documents found in the collection.")
        return

    # Flatten embedded 'host' document
    if 'host' in df.columns:
        host_df = pd.json_normalize(df['host'])
        df = pd.concat([df.drop(columns=['host']), host_df], axis=1)

    # Flatten embedded 'score' document
    if 'score' in df.columns:
        score_df = pd.json_normalize(df['score'])
        df = pd.concat([df.drop(columns=['score']), score_df], axis=1)

    # Drop MongoDB _id column
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Exported {len(df)} records to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
