import pandas as pd
import json
import re

def normalize_commodity(commodity_raw):
    """
    Normaliza commodities a categorías generales.
    Agrupa variaciones similares (ej: '32" TV', 'Smart TV' → 'TV')
    """
    if pd.isna(commodity_raw):
        return None
    
    commodity = str(commodity_raw).lower().strip()
    
    # Reglas de normalización por categorías
    normalization_rules = {
        'TV': [
            r'\btv\b', r'television', r'hdtv', r'\d+"?\s*(tv|hdtv|television)',
            r'apple tv', r'roku', r'chromecast', r'fire tv', r'smart tv',
            r'cable', r'netflix', r'hulu'
        ],
        'WiFi': [r'wi-fi', r'wifi', r'wireless internet', r'internet'],
        'Kitchen': [r'kitchen'],
        'Air conditioning': [r'air conditioning', r'\bac\b', r'central air', r'cooling'],
        'Heating': [r'heating', r'central heating', r'radiator', r'fireplace', r'wood burning'],
        'Washer': [r'washer', r'washing machine'],
        'Dryer': [r'dryer', r'drying machine'],
        'Parking': [r'parking', r'garage', r'free parking', r'street parking', r'paid parking'],
        'Pool': [r'pool', r'swimming pool', r'private pool', r'shared pool'],
        'Hot tub': [r'hot tub', r'jacuzzi'],
        'Gym': [r'gym', r'fitness', r'exercise equipment'],
        'Workspace': [r'workspace', r'dedicated workspace', r'laptop-friendly'],
        'Smoke alarm': [r'smoke alarm', r'smoke detector'],
        'Carbon monoxide alarm': [r'carbon monoxide', r'\bco\b alarm', r'\bco\b detector'],
        'Fire extinguisher': [r'fire extinguisher'],
        'First aid kit': [r'first aid'],
        'Lock': [r'lock', r'smart lock', r'lockbox', r'keypad', r'security'],
        'Coffee maker': [r'coffee', r'espresso', r'nespresso', r'keurig'],
        'Dishwasher': [r'dishwasher'],
        'Microwave': [r'microwave'],
        'Refrigerator': [r'refrigerator', r'fridge'],
        'Oven': [r'oven', r'stove', r'cooktop', r'range'],
        'BBQ grill': [r'bbq', r'grill', r'barbecue'],
        'Patio': [r'patio', r'balcony', r'terrace', r'deck'],
        'Garden': [r'garden', r'backyard', r'yard'],
        'Beach access': [r'beach', r'beachfront', r'waterfront', r'lake access'],
        'Pets allowed': [r'pet', r'dog', r'cat', r'pets allowed'],
        'Smoking allowed': [r'smoking allowed'],
        'Elevator': [r'elevator', r'lift'],
        'Wheelchair accessible': [r'wheelchair', r'accessible', r'disability', r'step-free'],
        'Crib': [r'crib', r'baby bed', r'pack.*play'],
        'High chair': [r'high chair', r'baby chair'],
        'Self check-in': [r'self check-in', r'keyless entry'],
        'Essentials': [r'essentials', r'towels', r'bed sheets', r'soap', r'toilet paper', r'shampoo'],
        'Hangers': [r'hangers', r'closet', r'wardrobe'],
        'Hair dryer': [r'hair dryer', r'hairdryer'],
        'Iron': [r'iron', r'ironing board'],
        'Sound system': [r'sound system', r'speaker', r'bluetooth speaker', r'stereo'],
        'Books': [r'books', r'reading material'],
        'Board games': [r'board games', r'games', r'video games'],
        'Long term stays': [r'long term', r'monthly'],
        'Host greets you': [r'host greets', r'host greeting'],
    }
    
    # Aplicar reglas en orden de prioridad
    for category, patterns in normalization_rules.items():
        for pattern in patterns:
            if re.search(pattern, commodity, re.IGNORECASE):
                return category
    
    # Si no coincide, clasificar como "Other"
    return 'Other'


def extract_and_normalize_amenities(
    input_csv='datasets/listings.csv', 
    output_csv='datasets/amenities_normalized.csv'
):
    """
    Extrae amenities del JSON y las normaliza.
    Genera CSV limpio listo para consumir en Hop.
    """
    print("Leyendo archivo de listings...")
    df = pd.read_csv(input_csv)
    
    print("Extrayendo y normalizando amenities...")
    records = []
    errors = 0
    
    for _, row in df.iterrows():
        try:
            # Parsear JSON
            amenities = json.loads(row['amenities'].replace("'", '"'))
            
            for amenity in amenities:
                commodity_raw = amenity.strip()
                commodity_normalized = normalize_commodity(commodity_raw)
                
                if commodity_normalized:  # Solo agregar si no es None
                    records.append({
                        'hosting_id': row['id'],
                        'commodity_raw': commodity_raw,
                        'commodity_normalized': commodity_normalized
                    })
        except Exception as e:
            errors += 1
            continue
    
    # Crear DataFrame
    df_result = pd.DataFrame(records)
    
    # Eliminar duplicados (mismo hosting + misma commodity normalizada)
    df_result = df_result.drop_duplicates(subset=['hosting_id', 'commodity_normalized'])
    
    # Exportar
    df_result.to_csv(output_csv, index=False)
    
    # Estadísticas
    print("\n" + "="*50)
    print("PROCESO COMPLETADO")
    print("="*50)
    print(f"Total registros exportados: {len(df_result):,}")
    print(f"Hostings procesados: {df_result['hosting_id'].nunique():,}")
    print(f"Commodities raw únicas: {df_result['commodity_raw'].nunique():,}")
    print(f"Commodities normalizadas únicas: {df_result['commodity_normalized'].nunique():,}")
    print(f"Errores durante parseo: {errors}")
    
    print(f"\nArchivo guardado: {output_csv}")
    
    # Top 10 commodities
    print("\nTop 10 commodities más comunes:")
    print(df_result['commodity_normalized'].value_counts().head(10))
    
    # Commodities en "Other"
    other_count = (df_result['commodity_normalized'] == 'Other').sum()
    if other_count > 0:
        print(f"\n{other_count} registros clasificados como 'Other'")
        print("Ejemplos de commodities sin clasificar:")
        other_examples = df_result[df_result['commodity_normalized'] == 'Other']['commodity_raw'].unique()[:10]
        for ex in other_examples:
            print(f"  - {ex}")
    
    return df_result


if __name__ == "__main__":
    print("="*50)
    print("NORMALIZACIÓN DE COMMODITIES")
    print("="*50)
    
    df = extract_and_normalize_amenities()
    
    print("\nCSV limpio listo para Hop ETL")