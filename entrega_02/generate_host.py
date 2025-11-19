import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================
# 1. LEER CSVs ORIGINALES
# ============================================
print("Leyendo datasets...")
df_listings = pd.read_csv('datasets/listings.csv')
df_reviews = pd.read_csv('datasets/reviews.csv')

print(f"Listings: {len(df_listings)}")
print(f"Reviews: {len(df_reviews)}")

# ============================================
# 2. EXTRAER DATOS BASE DE HOSPEDADORES
# ============================================
# Seleccionar campos relevantes y eliminar duplicados por host_id
df_hosts = df_listings[[
    'host_id', 
    'host_name',
    'host_response_time',
    'host_is_superhost',
    'calculated_host_listings_count'
]].drop_duplicates(subset=['host_id']).copy()

print(f"\nHospedadores únicos: {len(df_hosts)}")

# ============================================
# 3. CALCULAR AVG_SCORE POR HOST
# ============================================
# Obtener mapping listing_id -> host_id
listing_to_host = df_listings[['id', 'host_id']].rename(columns={'id': 'listing_id'})

# Merge reviews con listings para obtener host_id
df_reviews_with_host = df_reviews.merge(
    listing_to_host, 
    on='listing_id', 
    how='left'
)

# Calcular score promedio por host (simulado, ya que reviews.csv no tiene score)
# En reviews.csv real no hay puntuación numérica, así que la simularemos
# basándonos en sentiment analysis o asignando aleatoria pero coherente
def simular_score_from_comment(comment, review_id):
    """Simula score basado en longitud del comentario (proxy de satisfacción)"""
    if pd.isna(comment) or len(str(comment)) < 10:
        return np.random.choice([3.0, 3.5, 4.0], p=[0.1, 0.3, 0.6])
    
    # Comentarios largos tienden a ser más positivos
    longitud = len(str(comment))
    if longitud > 200:
        return np.random.choice([4.0, 4.5, 5.0], p=[0.2, 0.3, 0.5])
    elif longitud > 100:
        return np.random.choice([3.5, 4.0, 4.5], p=[0.3, 0.4, 0.3])
    else:
        return np.random.choice([3.0, 3.5, 4.0], p=[0.2, 0.4, 0.4])

df_reviews_with_host['score_simulado'] = df_reviews_with_host.apply(
    lambda row: simular_score_from_comment(row['comments'], row['id']),
    axis=1
)

# Agregar por host_id
avg_scores = df_reviews_with_host.groupby('host_id')['score_simulado'].mean().reset_index()
avg_scores.columns = ['host_id', 'avg_score']

# Merge con df_hosts
df_hosts = df_hosts.merge(avg_scores, on='host_id', how='left')

# Hosts sin reviews: score NULL
df_hosts['avg_score'] = df_hosts['avg_score'].round(2)

# ============================================
# 4. LIMPIAR Y NORMALIZAR DATOS
# ============================================
# Response time: normalizar valores
def normalizar_response_time(value):
    if pd.isna(value):
        return 'N/A'
    value = str(value).lower()
    if 'hour' in value or 'hora' in value:
        return 'within an hour'
    elif 'day' in value or 'día' in value or 'dia' in value:
        return 'within a day'
    elif 'few' in value:
        return 'within a few hours'
    else:
        return 'N/A'

df_hosts['response_time'] = df_hosts['host_response_time'].apply(normalizar_response_time)

# Superhost: convertir t/f a 1/0
def convertir_superhost(value):
    if pd.isna(value):
        return 0
    return 1 if str(value).lower() in ['t', 'true', '1'] else 0

df_hosts['superhost'] = df_hosts['host_is_superhost'].apply(convertir_superhost)

# Total hostings
df_hosts['total_hostings'] = df_hosts['calculated_host_listings_count'].fillna(1).astype(int)

# ============================================
# 5. SIMULAR CAMBIOS TEMPORALES (SCD2)
# ============================================
# Obtener fechas de reviews para cada host
host_review_dates = df_reviews_with_host.groupby('host_id')['date'].agg(['min', 'max']).reset_index()
host_review_dates.columns = ['host_id', 'fecha_primera_review', 'fecha_ultima_review']

df_hosts = df_hosts.merge(host_review_dates, on='host_id', how='left')

# Convertir a datetime
df_hosts['fecha_primera_review'] = pd.to_datetime(df_hosts['fecha_primera_review'])
df_hosts['fecha_ultima_review'] = pd.to_datetime(df_hosts['fecha_ultima_review'])

# Calcular años activo
df_hosts['anos_activo'] = (
    df_hosts['fecha_ultima_review'] - df_hosts['fecha_primera_review']
).dt.days / 365

df_hosts['anos_activo'] = df_hosts['anos_activo'].fillna(0)

# ============================================
# 6. CREAR VERSIONES SCD2
# ============================================
df_scd2 = []

for _, row in df_hosts.iterrows():
    if pd.isna(row['fecha_primera_review']):
        # Host sin reviews: solo versión actual
        version = {
            'host_id': int(row['host_id']),
            'response_time': row['response_time'],
            'avg_score': row['avg_score'] if not pd.isna(row['avg_score']) else None,
            'total_hostings': int(row['total_hostings']),
            'superhost': int(row['superhost']),
            'data_empezou_valer': datetime.now().date(),
            'data_deixou_valer': None,
            'actual': 1
        }
        df_scd2.append(version)
        continue
    
    # Versión inicial
    version_inicial = {
        'host_id': int(row['host_id']),
        'response_time': row['response_time'],
        'avg_score': row['avg_score'] if not pd.isna(row['avg_score']) else None,
        'total_hostings': int(row['total_hostings']),
        'superhost': int(row['superhost']),
        'data_empezou_valer': row['fecha_primera_review'].date(),
        'data_deixou_valer': None,
        'actual': 1
    }
    
    # Si estuvo activo >3 años, simular cambio (se volvió superhost o aumentó hostings)
    if row['anos_activo'] > 3:
        fecha_cambio = row['fecha_primera_review'] + (
            row['fecha_ultima_review'] - row['fecha_primera_review']
        ) / 2
        
        # Versión histórica
        version_historica = version_inicial.copy()
        version_historica['data_deixou_valer'] = fecha_cambio.date()
        version_historica['actual'] = 0
        df_scd2.append(version_historica)
        
        # Versión actual (cambios: +hostings, posible superhost)
        version_actual = version_inicial.copy()
        version_actual['total_hostings'] = int(row['total_hostings'] * 1.5)  # Aumentó hostings
        version_actual['superhost'] = 1 if np.random.random() > 0.3 else version_actual['superhost']  # 70% se vuelven superhosts
        version_actual['avg_score'] = round(min(5.0, row['avg_score'] + 0.2), 2) if not pd.isna(row['avg_score']) else None
        version_actual['data_empezou_valer'] = fecha_cambio.date()
        df_scd2.append(version_actual)
    else:
        df_scd2.append(version_inicial)

df_final = pd.DataFrame(df_scd2)

# ============================================
# 7. FORMATEAR Y EXPORTAR
# ============================================
# Convertir fechas a string
df_final['data_empezou_valer'] = pd.to_datetime(df_final['data_empezou_valer'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
df_final['data_deixou_valer'] = pd.to_datetime(df_final['data_deixou_valer'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

# Ordenar
df_final = df_final.sort_values(['host_id', 'data_empezou_valer'])

# Exportar
df_final.to_csv('datasets/dim_hospedador_scd2.csv', index=False, na_rep='')

print("\n" + "="*50)
print("DATASET GENERADO: dim_hospedador_scd2.csv")
print("="*50)
print(f"Total registros: {len(df_final)}")
print(f"Hospedadores únicos: {df_final['host_id'].nunique()}")
print(f"Registros históricos (actual=0): {(df_final['actual']==0).sum()}")
print(f"Registros actuales (actual=1): {(df_final['actual']==1).sum()}")
print(f"\nDistribución Superhost:")
print(df_final[df_final['actual']==1]['superhost'].value_counts())
print(f"\nTotal hostings promedio: {df_final[df_final['actual']==1]['total_hostings'].mean():.1f}")
print(f"Score promedio: {df_final[df_final['actual']==1]['avg_score'].mean():.2f}")