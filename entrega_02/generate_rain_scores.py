import pandas as pd
import numpy as np
from datetime import datetime
import re

def calculate_sentiment_score(comment):
    """
    Calcula score de sentimiento (1.0 - 5.0) basado en palabras clave.
    
    Args:
        comment: str, texto del comentario
    
    Returns:
        float: score entre 1.00 y 5.00
    """
    if pd.isna(comment) or len(str(comment).strip()) < 10:
        return 3.0  # Score neutro para comentarios vacíos/cortos
    
    comment = str(comment).lower()
    
    # Palabras positivas (cada una suma +0.5)
    positive_keywords = [
        'amazing', 'excellent', 'perfect', 'wonderful', 'great', 'fantastic',
        'loved', 'beautiful', 'clean', 'recommend', 'best', 'awesome',
        'incredible', 'outstanding', 'superb', 'lovely', 'comfortable',
        'friendly', 'helpful', 'spacious', 'cozy', 'stunning', 'exceptional'
    ]
    
    # Palabras negativas (cada una resta -0.7)
    negative_keywords = [
        'terrible', 'horrible', 'worst', 'dirty', 'bad', 'disappointing',
        'poor', 'never', 'awful', 'noisy', 'uncomfortable', 'rude',
        'problem', 'issues', 'broke', 'smelly', 'unsafe', 'scam',
        'disgusting', 'nightmare', 'avoid', 'unacceptable'
    ]
    
    # Contar coincidencias
    pos_count = sum(1 for word in positive_keywords if word in comment)
    neg_count = sum(1 for word in negative_keywords if word in comment)
    
    # Calcular score base (3.0) + ajustes
    score = 3.0 + (pos_count * 0.5) - (neg_count * 0.7)
    
    # Limitar a rango [1.0, 5.0]
    score = max(1.0, min(5.0, score))
    
    return round(score, 2)


def generate_rain_mm(date):
    """
    Genera datos realistas de lluvia basados en la fecha y estacionalidad.
    
    Args:
        date: datetime object
    
    Returns:
        float: milímetros de lluvia (0.00 - 45.00)
    """
    month = date.month
    
    # Probabilidad de lluvia según estación (España/Europa)
    # Meses lluviosos: Octubre-Mayo
    # Meses secos: Junio-Septiembre
    if month in [10, 11, 12, 1, 2, 3, 4, 5]:
        rain_probability = 0.35  # 35% en temporada lluviosa
    else:  # Jun-Sep (verano)
        rain_probability = 0.10  # 10% en verano
    
    # Determinar si llueve ese día
    if np.random.random() > rain_probability:
        return 0.0
    
    # Generar cantidad de lluvia con distribución realista
    intensity = np.random.random()
    
    if intensity < 0.6:  # 60% - Lluvia ligera
        rain_mm = np.random.uniform(0.1, 5.0)
    elif intensity < 0.9:  # 30% - Lluvia moderada
        rain_mm = np.random.uniform(5.0, 20.0)
    else:  # 10% - Lluvia intensa
        rain_mm = np.random.uniform(20.0, 45.0)
    
    return round(rain_mm, 2)


def enrich_reviews(input_reviews, input_listings, input_places, output_file):
    """
    Lee reviews.csv, listings.csv y places.csv, añade columnas SCORE, RAIN_MM, HOST_ID y PLACE_ID, 
    y guarda resultado.
    
    Args:
        input_reviews: ruta al CSV de reviews
        input_listings: ruta al CSV de listings
        input_places: ruta al CSV de places
        output_file: ruta al CSV de salida
    """
    print(f"Leyendo archivos...")
    print(f"  - Reviews: {input_reviews}")
    print(f"  - Listings: {input_listings}")
    print(f"  - Places: {input_places}")
    
    # Leer CSVs
    df_reviews = pd.read_csv(input_reviews, parse_dates=['date'])
    df_listings = pd.read_csv(input_listings)
    df_places = pd.read_csv(input_places)
    
    print(f"\n{len(df_reviews)} reviews cargadas")
    print(f"{len(df_listings)} listings cargados")
    print(f"{len(df_places)} places cargados")
    print(f"\nColumnas reviews originales: {list(df_reviews.columns)}")

    print("\nGenerando PLACE_IDs...")

    df_places['PLACE_ID'] = (
        df_places['STREET'].str.replace(' ', '', regex=False) + '_' + 
        df_places['CITY'].str.replace(' ', '', regex=False) + '_' + 
        df_places['COUNTRY'].str.replace(' ', '', regex=False)
    )
    
    print(f"  {len(df_places)} PLACE_IDs generados")
    print(f"  PLACE_IDs únicos: {df_places['PLACE_ID'].nunique()}")
    
    # Mostrar ejemplos de PLACE_IDs generados
    print(f"\n  Ejemplos de PLACE_IDs generados:")
    for place_id in df_places['PLACE_ID'].head(10):
        print(f"    - {place_id}")

    print("\nAgregando HOST_ID...")
    
    # Crear mapeo listing_id -> host_id
    listing_to_host = df_listings[['id', 'host_id']].rename(columns={'id': 'listing_id'})
    
    # Merge para agregar host_id
    df_enriched = df_reviews.merge(
        listing_to_host,
        on='listing_id',
        how='left'
    )
    
    print(f"Reviews con HOST_ID: {df_enriched['host_id'].notna().sum()}")
    print(f"Reviews sin HOST_ID: {df_enriched['host_id'].isna().sum()}")

    print("\nAsignando PLACE_ID aleatorio...")
    
    # Obtener lista de PLACE_IDs disponibles
    place_ids = df_places['PLACE_ID'].tolist()
    
    # Asignar aleatoriamente un PLACE_ID a cada review
    np.random.seed(42)  # Para reproducibilidad
    df_enriched['PLACE_ID'] = np.random.choice(place_ids, size=len(df_enriched))
    
    print(f"  PLACE_IDs asignados: {len(df_enriched)}")
    print(f"  Places únicos usados: {df_enriched['PLACE_ID'].nunique()}")

    print("\nCalculando scores de sentimiento...")
    df_enriched['score'] = df_enriched['comments'].apply(calculate_sentiment_score)

    print("Generando datos de lluvia...")
    df_enriched['rain_mm'] = df_enriched['date'].apply(generate_rain_mm)

    # Convertir date a string
    df_enriched['date'] = df_enriched['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Renombrar columnas a mayúsculas para consistencia
    df_enriched = df_enriched.rename(columns={
        'id': 'REVIEW_ID',
        'listing_id': 'HOSTING_ID',
        'host_id': 'HOST_ID',
        'date': 'REVIEW_DATE',
        'reviewer_id': 'REVIEWER_ID',
        'reviewer_name': 'REVIEWER_NAME',
        'comments': 'COMMENTS',
        'score': 'SCORE',
        'rain_mm': 'RAIN_MM'
    })
    
    # Reordenar columnas
    column_order = [
        'REVIEW_ID',
        'HOSTING_ID',
        'HOST_ID',
        'REVIEWER_ID',
        'PLACE_ID',
        'REVIEWER_NAME',
        'REVIEW_DATE',
        'COMMENTS',
        'SCORE',
        'RAIN_MM'
    ]
    df_enriched = df_enriched[column_order]
    
    # Guardar CSV enriquecido
    df_enriched.to_csv(output_file, index=False)
    print(f"\nArchivo reviews guardado: {output_file}")
    
    # Reordenar columnas de places para que PLACE_ID sea la primera
    df_places = df_places[['PLACE_ID', 'STREET', 'CITY', 'COUNTRY', 'LATITUD', 'LONGITUD']]
    
    # Guardar places actualizado
    df_places.to_csv(input_places, index=False)
    print(f"Archivo places actualizado: {input_places}")

    print("\n" + "="*60)
    print("ESTADÍSTICAS GENERADAS")
    print("="*60)
    
    print(f"\nTOTAL REGISTROS: {len(df_enriched)}")
    print(f"COLUMNAS: {list(df_enriched.columns)}")
    
    print("\nSCORE (Sentimiento):")
    print(f"   Media: {df_enriched['SCORE'].mean():.2f}")
    print(f"   Mediana: {df_enriched['SCORE'].median():.2f}")
    print(f"   Min: {df_enriched['SCORE'].min():.2f}")
    print(f"   Max: {df_enriched['SCORE'].max():.2f}")
    print(f"   Desv. Std: {df_enriched['SCORE'].std():.2f}")
    print(f"\n   Distribución:")
    print(f"   - Muy negativo (1.0-2.0): {len(df_enriched[df_enriched['SCORE'] < 2.0])} ({len(df_enriched[df_enriched['SCORE'] < 2.0])/len(df_enriched)*100:.1f}%)")
    print(f"   - Negativo (2.0-3.0):     {len(df_enriched[(df_enriched['SCORE'] >= 2.0) & (df_enriched['SCORE'] < 3.0)])} ({len(df_enriched[(df_enriched['SCORE'] >= 2.0) & (df_enriched['SCORE'] < 3.0)])/len(df_enriched)*100:.1f}%)")
    print(f"   - Neutro (3.0-4.0):       {len(df_enriched[(df_enriched['SCORE'] >= 3.0) & (df_enriched['SCORE'] < 4.0)])} ({len(df_enriched[(df_enriched['SCORE'] >= 3.0) & (df_enriched['SCORE'] < 4.0)])/len(df_enriched)*100:.1f}%)")
    print(f"   - Positivo (4.0-5.0):     {len(df_enriched[df_enriched['SCORE'] >= 4.0])} ({len(df_enriched[df_enriched['SCORE'] >= 4.0])/len(df_enriched)*100:.1f}%)")
    
    print("\nRAIN_MM (Lluvia):")
    rainy_days = df_enriched[df_enriched['RAIN_MM'] > 0]
    print(f"   Días con lluvia: {len(rainy_days)} de {len(df_enriched)} ({len(rainy_days)/len(df_enriched)*100:.1f}%)")
    if len(rainy_days) > 0:
        print(f"   Media (días con lluvia): {rainy_days['RAIN_MM'].mean():.2f} mm")
        print(f"   Mediana (días con lluvia): {rainy_days['RAIN_MM'].median():.2f} mm")
        print(f"   Máximo: {rainy_days['RAIN_MM'].max():.2f} mm")
        print(f"\n   Distribución de intensidad:")
        print(f"   - Ligera (0.1-5 mm):    {len(rainy_days[rainy_days['RAIN_MM'] < 5])} ({len(rainy_days[rainy_days['RAIN_MM'] < 5])/len(rainy_days)*100:.1f}%)")
        print(f"   - Moderada (5-20 mm):   {len(rainy_days[(rainy_days['RAIN_MM'] >= 5) & (rainy_days['RAIN_MM'] < 20)])} ({len(rainy_days[(rainy_days['RAIN_MM'] >= 5) & (rainy_days['RAIN_MM'] < 20)])/len(rainy_days)*100:.1f}%)")
        print(f"   - Intensa (20-45 mm):   {len(rainy_days[rainy_days['RAIN_MM'] >= 20])} ({len(rainy_days[rainy_days['RAIN_MM'] >= 20])/len(rainy_days)*100:.1f}%)")
    
    print("\nHOST_ID:")
    print(f"   Reviews con HOST_ID: {df_enriched['HOST_ID'].notna().sum()} ({df_enriched['HOST_ID'].notna().sum()/len(df_enriched)*100:.1f}%)")
    print(f"   Reviews sin HOST_ID: {df_enriched['HOST_ID'].isna().sum()} ({df_enriched['HOST_ID'].isna().sum()/len(df_enriched)*100:.1f}%)")
    print(f"   Hosts únicos: {df_enriched['HOST_ID'].nunique()}")
    
    print("\nPLACE_ID:")
    print(f"   Reviews con PLACE_ID: {len(df_enriched)}")
    print(f"   Places únicos usados: {df_enriched['PLACE_ID'].nunique()}")
    print(f"   Places disponibles: {len(place_ids)}")
    
    # Mostrar ejemplos de PLACE_IDs más usados
    print(f"\n   Top 10 PLACE_IDs más usados:")
    sample_places = df_enriched['PLACE_ID'].value_counts().head(10)
    for place_id, count in sample_places.items():
        print(f"      {place_id}: {count} reviews")
    
    # Mostrar ejemplos
    print("\n" + "="*60)
    print("EJEMPLOS DE REGISTROS ENRIQUECIDOS")
    print("="*60)
    sample = df_enriched[['REVIEW_ID', 'HOSTING_ID', 'HOST_ID', 'PLACE_ID', 'REVIEW_DATE', 'SCORE', 'RAIN_MM', 'COMMENTS']].head(5)
    for idx, row in sample.iterrows():
        comment_preview = str(row['COMMENTS'])[:60] + "..." if len(str(row['COMMENTS'])) > 60 else str(row['COMMENTS'])
        print(f"\nID: {row['REVIEW_ID']} | Hosting: {row['HOSTING_ID']} | Host: {row['HOST_ID']}")
        print(f"Place: {row['PLACE_ID']}")
        print(f"Fecha: {row['REVIEW_DATE']} | Score: {row['SCORE']:.2f} | Lluvia: {row['RAIN_MM']:.2f}mm")
        print(f"Comentario: {comment_preview}")
        print("-" * 120)
    
    return df_enriched


if __name__ == "__main__":
    # Configuración
    INPUT_REVIEWS = 'datasets/reviews.csv'
    INPUT_LISTINGS = 'datasets/listings.csv'
    INPUT_PLACES = 'datasets/places.csv'
    OUTPUT_FILE = 'datasets/reviews_enriched.csv'
    
    # Establecer semilla para reproducibilidad
    np.random.seed(42)
    
    # Ejecutar enriquecimiento
    df_enriched = enrich_reviews(INPUT_REVIEWS, INPUT_LISTINGS, INPUT_PLACES, OUTPUT_FILE)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print(f"Archivo reviews listo: {OUTPUT_FILE}")
    print(f"Archivo places actualizado: {INPUT_PLACES}")