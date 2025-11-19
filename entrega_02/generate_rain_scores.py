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
    # La mayoría de lluvias son ligeras, pocas son intensas
    intensity = np.random.random()
    
    if intensity < 0.6:  # 60% - Lluvia ligera
        rain_mm = np.random.uniform(0.1, 5.0)
    elif intensity < 0.9:  # 30% - Lluvia moderada
        rain_mm = np.random.uniform(5.0, 20.0)
    else:  # 10% - Lluvia intensa
        rain_mm = np.random.uniform(20.0, 45.0)
    
    return round(rain_mm, 2)


def enrich_reviews(input_file, output_file):
    """
    Lee reviews.csv, añade columnas SCORE y RAIN_MM, y guarda resultado.
    
    Args:
        input_file: ruta al CSV original
        output_file: ruta al CSV de salida
    """
    print(f"Leyendo archivo: {input_file}")
    
    # Leer CSV original
    df = pd.read_csv(input_file, parse_dates=['date'])
    
    print(f"{len(df)} registros cargados")
    print(f"\nColumnas originales: {list(df.columns)}")
    
    # Convert to datetime if necessary (keep as datetime for calculations)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Generar columna SCORE
    print("\nCalculando scores de sentimiento...")
    df['score'] = df['comments'].apply(calculate_sentiment_score)
    
    # Generar columna RAIN_MM (use datetime objects)
    print("Generando datos de lluvia...")
    df['rain_mm'] = df['date'].apply(generate_rain_mm)
    
    # Now convert date to string format for output
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Guardar CSV enriquecido
    df.to_csv(output_file, index=False)
    print(f"\nArchivo guardado: {output_file}")
    
    # Estadísticas
    print("\n" + "="*60)
    print("ESTADÍSTICAS GENERADAS")
    print("="*60)
    
    print("\nSCORE (Sentimiento):")
    print(f"   Media: {df['score'].mean():.2f}")
    print(f"   Mediana: {df['score'].median():.2f}")
    print(f"   Min: {df['score'].min():.2f}")
    print(f"   Max: {df['score'].max():.2f}")
    print(f"   Desv. Std: {df['score'].std():.2f}")
    print(f"\n   Distribución:")
    print(f"   - Muy negativo (1.0-2.0): {len(df[df['score'] < 2.0])} ({len(df[df['score'] < 2.0])/len(df)*100:.1f}%)")
    print(f"   - Negativo (2.0-3.0):     {len(df[(df['score'] >= 2.0) & (df['score'] < 3.0)])} ({len(df[(df['score'] >= 2.0) & (df['score'] < 3.0)])/len(df)*100:.1f}%)")
    print(f"   - Neutro (3.0-4.0):       {len(df[(df['score'] >= 3.0) & (df['score'] < 4.0)])} ({len(df[(df['score'] >= 3.0) & (df['score'] < 4.0)])/len(df)*100:.1f}%)")
    print(f"   - Positivo (4.0-5.0):     {len(df[df['score'] >= 4.0])} ({len(df[df['score'] >= 4.0])/len(df)*100:.1f}%)")
    
    print("\nRAIN_MM (Lluvia):")
    rainy_days = df[df['rain_mm'] > 0]
    print(f"   Días con lluvia: {len(rainy_days)} de {len(df)} ({len(rainy_days)/len(df)*100:.1f}%)")
    if len(rainy_days) > 0:
        print(f"   Media (días con lluvia): {rainy_days['rain_mm'].mean():.2f} mm")
        print(f"   Mediana (días con lluvia): {rainy_days['rain_mm'].median():.2f} mm")
        print(f"   Máximo: {rainy_days['rain_mm'].max():.2f} mm")
        print(f"\n   Distribución de intensidad:")
        print(f"   - Ligera (0.1-5 mm):    {len(rainy_days[rainy_days['rain_mm'] < 5])} ({len(rainy_days[rainy_days['rain_mm'] < 5])/len(rainy_days)*100:.1f}%)")
        print(f"   - Moderada (5-20 mm):   {len(rainy_days[(rainy_days['rain_mm'] >= 5) & (rainy_days['rain_mm'] < 20)])} ({len(rainy_days[(rainy_days['rain_mm'] >= 5) & (rainy_days['rain_mm'] < 20)])/len(rainy_days)*100:.1f}%)")
        print(f"   - Intensa (20-45 mm):   {len(rainy_days[rainy_days['rain_mm'] >= 20])} ({len(rainy_days[rainy_days['rain_mm'] >= 20])/len(rainy_days)*100:.1f}%)")
    
    # Mostrar ejemplos
    print("\nEJEMPLOS DE REGISTROS ENRIQUECIDOS:")
    print("-" * 120)
    sample = df[['id', 'date', 'comments', 'score', 'rain_mm']].head(5)
    for idx, row in sample.iterrows():
        comment_preview = str(row['comments'])[:60] + "..." if len(str(row['comments'])) > 60 else str(row['comments'])
        print(f"ID: {row['id']} | {row['date']} | Score: {row['score']:.2f} | Lluvia: {row['rain_mm']:.2f}mm")
        print(f"   Comentario: {comment_preview}")
        print("-" * 120)
    
    return df


if __name__ == "__main__":
    # Configuración
    INPUT_FILE = 'datasets/reviews.csv'
    OUTPUT_FILE = 'datasets/reviews_enriched.csv'
    
    # Establecer semilla para reproducibilidad (opcional)
    np.random.seed(42)
    
    # Ejecutar enriquecimiento
    df_enriched = enrich_reviews(INPUT_FILE, OUTPUT_FILE)
    
    print("\nProceso completado exitosamente!")
    print(f"Archivo listo para usar en Apache Hop: {OUTPUT_FILE}")