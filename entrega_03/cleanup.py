"""
Análisis y Limpieza del dataset de Airbnb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# CARGAR DATOS
# =============================================================================

df = pd.read_csv("datasets/listings.csv")

# Limpiar precio (corregido el escape)
df['precio'] = df['price'].replace(r'[\$,]', '', regex=True).astype(float)

print(f"Total de listings: {len(df)}")
print(f"Columnas: {len(df.columns)}")

# =============================================================================
# 1.  VALORES NULOS
# =============================================================================

print("\n" + "="*50)
print("VALORES NULOS")
print("="*50)

nulos = df.isnull().sum()
nulos_pct = (nulos / len(df) * 100).round(1)
nulos_df = pd.DataFrame({'nulos': nulos, '%': nulos_pct})
nulos_df = nulos_df[nulos_df['nulos'] > 0].sort_values('%', ascending=False)
print(nulos_df.head(15))

# Nulos en scores
print("\n--- Nulos en Review Scores ---")
score_cols = [c for c in df.columns if 'review_scores' in c]
for col in score_cols:
    n = df[col].isnull().sum()
    print(f"{col}: {n} ({n/len(df)*100:.1f}%)")

# =============================================================================
# 2.  OUTLIERS EN PRECIOS
# =============================================================================

print("\n" + "="*50)
print("OUTLIERS EN PRECIOS")
print("="*50)

print(f"\nMedia: ${df['precio'].mean():.2f}")
print(f"Mediana: ${df['precio'].median():.2f}")
print(f"Mínimo: ${df['precio'].min():.2f}")
print(f"Máximo: ${df['precio'].max():.2f}")

Q1 = df['precio'].quantile(0.25)
Q3 = df['precio'].quantile(0.75)
IQR = Q3 - Q1
limite_inf = Q1 - 1.5 * IQR
limite_sup = Q3 + 1.5 * IQR

outliers = df[(df['precio'] < limite_inf) | (df['precio'] > limite_sup)]
print(f"\nQ1: ${Q1:.2f}, Q3: ${Q3:.2f}")
print(f"Límites: ${limite_inf:.2f} - ${limite_sup:.2f}")
print(f"Outliers detectados: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

if len(outliers) > 0:
    print("\nOutliers:")
    print(outliers[['id', 'name', 'precio', 'room_type']].head(10))

# =============================================================================
# 3. LIMPIEZA DE DATOS
# =============================================================================

print("\n" + "="*50)
print("LIMPIEZA DE DATOS")
print("="*50)

df_clean = df.copy()
print(f"\nRegistros iniciales: {len(df_clean)}")

# 3.1 Eliminar columnas con 100% nulos o inútiles
cols_eliminar = ['calendar_updated', 'license', 'neighbourhood_group_cleansed']
df_clean = df_clean.drop(columns=cols_eliminar, errors='ignore')
print(f"Columnas eliminadas (100% nulos): {cols_eliminar}")

# 3.2 Eliminar outliers de precio
df_clean = df_clean[(df_clean['precio'] >= limite_inf) & (df_clean['precio'] <= limite_sup)]
print(f"Registros tras eliminar outliers de precio: {len(df_clean)}")

# 3.3 Tratar nulos en review scores
# Opción A: Eliminar filas sin ratings
# df_clean = df_clean. dropna(subset=['review_scores_rating'])

# Opción B: Rellenar con la mediana (más conservador)
for col in score_cols:
    mediana = df_clean[col].median()
    df_clean[col] = df_clean[col].fillna(mediana)
print(f"Nulos en scores rellenados con mediana")

# 3.4 Rellenar otros nulos importantes
# Bedrooms y beds: rellenar con mediana
for col in ['bedrooms', 'beds']:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())

# Host response rate: rellenar con 0 (asumimos no responde)
if 'host_response_rate' in df_clean.columns:
    df_clean['host_response_rate_clean'] = df_clean['host_response_rate'].replace('%', '', regex=True)
    df_clean['host_response_rate_clean'] = pd.to_numeric(df_clean['host_response_rate_clean'], errors='coerce').fillna(0)

# 3.5 Convertir variables categóricas
df_clean['host_is_superhost'] = df_clean['host_is_superhost'].map({'t': 1, 'f': 0}).fillna(0)
df_clean['instant_bookable'] = df_clean['instant_bookable'].map({'t': 1, 'f': 0}).fillna(0)

# 3.6 Eliminar columnas de texto innecesarias para análisis
cols_texto = ['listing_url', 'scrape_id', 'last_scraped', 'source', 'description', 
              'neighborhood_overview', 'picture_url', 'host_url', 'host_thumbnail_url',
              'host_picture_url', 'host_verifications', 'amenities', 'calendar_last_scraped']
df_clean = df_clean.drop(columns=[c for c in cols_texto if c in df_clean.columns], errors='ignore')

print(f"\nRegistros finales: {len(df_clean)}")
print(f"Columnas finales: {len(df_clean.columns)}")

# =============================================================================
# 4. VERIFICACIÓN POST-LIMPIEZA
# =============================================================================

print("\n" + "="*50)
print("VERIFICACIÓN POST-LIMPIEZA")
print("="*50)

# Nulos restantes
nulos_post = df_clean.isnull().sum()
nulos_post = nulos_post[nulos_post > 0]
print(f"\nColumnas con nulos restantes: {len(nulos_post)}")
if len(nulos_post) > 0:
    print(nulos_post. sort_values(ascending=False).head(10))

# Estadísticas de precio post-limpieza
print(f"\n--- Precio tras limpieza ---")
print(f"Media: ${df_clean['precio'].mean():.2f}")
print(f"Mediana: ${df_clean['precio'].median():.2f}")
print(f"Min: ${df_clean['precio']. min():.2f}")
print(f"Max: ${df_clean['precio'].max():.2f}")

# Scores post-limpieza
print(f"\n--- Scores tras limpieza ---")
print(f"Nulos en rating: {df_clean['review_scores_rating'].isnull().sum()}")
print(f"Rating medio: {df_clean['review_scores_rating'].mean():.2f}")

# =============================================================================
# 5. GUARDAR DATOS LIMPIOS
# =============================================================================

df_clean.to_csv("datasets/listings_clean.csv", index=False)
print(f"\nDatos limpios guardados en 'datasets/listings_clean.csv'")

# =============================================================================
# 6. VISUALIZACIONES
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Boxplot precios (antes vs después)
axes[0,0].boxplot([df['precio'].dropna(), df_clean['precio']], labels=['Original', 'Limpio'])
axes[0,0]. set_title('Precios: Original vs Limpio')
axes[0,0].set_ylabel('Precio ($)')

# Histograma precios limpios
axes[0,1].hist(df_clean['precio'], bins=30, edgecolor='black', color='green', alpha=0.7)
axes[0,1].set_title('Distribución Precios (Limpio)')
axes[0,1].set_xlabel('Precio ($)')

# Distribución de ratings
df_clean['review_scores_rating'].hist(ax=axes[1,0], bins=20, edgecolor='black', color='blue', alpha=0.7)
axes[1,0].set_title('Distribución Ratings (Limpio)')
axes[1,0].set_xlabel('Rating')

# Precio por tipo de habitación
df_clean. boxplot(column='precio', by='room_type', ax=axes[1,1])
axes[1,1].set_title('Precio por Tipo de Habitación')
axes[1,1].set_xlabel('Tipo')
axes[1,1].set_ylabel('Precio ($)')
plt.suptitle('')

plt.tight_layout()
plt.savefig('analisis_limpieza.png', dpi=150)
plt.show()

# =============================================================================
# 7. RESUMEN FINAL
# =============================================================================

print("\n" + "="*50)
print("RESUMEN FINAL")
print("="*50)
print(f"{'Métrica':<30} {'Original':>10} {'Limpio':>10}")
print("-"*50)
print(f"{'Registros':<30} {len(df):>10} {len(df_clean):>10}")
print(f"{'Columnas':<30} {len(df.columns):>10} {len(df_clean.columns):>10}")
print(f"{'Precio medio':<30} ${df['precio'].mean():>9.2f} ${df_clean['precio'].mean():>9.2f}")
print(f"{'Precio máximo':<30} ${df['precio'].max():>9.2f} ${df_clean['precio'].max():>9.2f}")
print(f"{'Nulos en rating':<30} {df['review_scores_rating'].isnull().sum():>10} {df_clean['review_scores_rating'].isnull().sum():>10}")