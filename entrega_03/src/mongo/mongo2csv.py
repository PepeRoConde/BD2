#!/usr/bin/env python3
import pandas as pd
from pymongo import MongoClient
import os

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "airbnb"
COLLECTION_NAME = "listings"
OUTPUT_FILE = "dataset/merged.csv"
CENTRALITY_COLUMN = "centrality"

def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch centrality values sorted by row_id
    cursor = collection.find({}, {"row_id": 1, CENTRALITY_COLUMN: 1}).sort("row_id", 1)
    df_centrality = pd.DataFrame(list(cursor))
    
    if df_centrality.empty:
        print("No documents found in the collection.")
        return
    
    # Ensure we have centrality column
    if CENTRALITY_COLUMN not in df_centrality.columns:
        print(f"Column '{CENTRALITY_COLUMN}' not found in the collection.")
        return
    
    # Extract just the centrality column values (already sorted by row_id from MongoDB)
    centrality_values = df_centrality[CENTRALITY_COLUMN].values
    
    # Check if the CSV file exists
    if os.path.exists(OUTPUT_FILE):
        # Read existing CSV
        df_existing = pd.read_csv(OUTPUT_FILE)
        
        # Check if number of rows match
        if len(df_existing) != len(centrality_values):
            print(f"Warning: Row count mismatch. CSV has {len(df_existing)} rows, MongoDB has {len(centrality_values)} records.")
            print("Proceeding with available data (will truncate to min length)...")
            min_length = min(len(df_existing), len(centrality_values))
            centrality_values = centrality_values[:min_length]
            df_existing = df_existing.iloc[:min_length]
        
        # Check if centrality column already exists
        if CENTRALITY_COLUMN in df_existing.columns:
            # Replace existing centrality column
            df_existing[CENTRALITY_COLUMN] = centrality_values
        else:
            # Add centrality column
            df_existing[CENTRALITY_COLUMN] = centrality_values
        
        # Save back to CSV
        df_existing.to_csv(OUTPUT_FILE, index=False)
        print(f"Added/updated '{CENTRALITY_COLUMN}' column to {OUTPUT_FILE}")
        print(f"Processed {len(df_existing)} rows")
    else:
        # Create new CSV with just centrality (no row_id column)
        df_output = pd.DataFrame({CENTRALITY_COLUMN: centrality_values})
        df_output.to_csv(OUTPUT_FILE, index=False)
        print(f"Created new file {OUTPUT_FILE} with '{CENTRALITY_COLUMN}' column")
        print(f"Processed {len(centrality_values)} rows")

if __name__ == "__main__":
    main()
