import pandas as pd
import json

df = pd.read_csv('datasets/listings.csv')

# Solo parsear el JSON a formato plano
records = []
for _, row in df.iterrows():
    try:
        amenities = json.loads(row['amenities'].replace("'", '"'))
        for amenity in amenities:
            records.append({
                'hosting_id': row['id'],
                'commodity_raw': amenity.strip()
            })
    except:
        pass

df_flat = pd.DataFrame(records)
df_flat.to_csv('datasets/amenities_raw.csv', index=False)
print(f"{len(df_flat)} registros exportados")

def obtain_unique_commodities(input_csv='datasets/amenities_raw.csv', output_csv='datasets/dim_commodity.csv'):
    df = pd.read_csv(input_csv)
    unique_commodities = df['commodity_raw'].dropna().unique()
    
    df_commodities = pd.DataFrame({
        'commodity_id': range(1, len(unique_commodities) + 1),
        'commodity_name': unique_commodities
    })
    
    df_commodities.to_csv(output_csv, index=False)
    print(f"{len(df_commodities)} commodities únicos exportados a {output_csv}")

if __name__ == "__main__":
    obtain_unique_commodities()