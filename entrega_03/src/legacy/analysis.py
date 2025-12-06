"""
Análisis simple del dataset de Airbnb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# CARGAR DATOS
# =============================================================================

df = pd.read_csv("datasets/listings.csv")

# Limpiar precio (quitar $ y convertir a número)
df['precio'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

print(f"Total de listings: {len(df)}")
print(f"Columnas: {len(df.columns)}")

# =============================================================================
# 1. VALORES NULOS
# =============================================================================

print("\n" + "="*50)
print("VALORES NULOS")
print("="*50)

# Nulos generales
nulos = df.isnull().sum()
nulos_pct = (nulos / len(df) * 100).round(1)
nulos_df = pd.DataFrame({'nulos': nulos, '%': nulos_pct})
nulos_df = nulos_df[nulos_df['nulos'] > 0]. sort_values('%', ascending=False)
print(nulos_df. head(15))

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

# Estadísticas básicas
print(f"\nMedia: ${df['precio'].mean():.2f}")
print(f"Mediana: ${df['precio'].median():.2f}")
print(f"Mínimo: ${df['precio'].min():.2f}")
print(f"Máximo: ${df['precio'].max():.2f}")

# Método IQR
Q1 = df['precio'].quantile(0.25)
Q3 = df['precio'].quantile(0.75)
IQR = Q3 - Q1
limite_inf = Q1 - 1.5 * IQR
limite_sup = Q3 + 1.5 * IQR

outliers = df[(df['precio'] < limite_inf) | (df['precio'] > limite_sup)]
print(f"\nQ1: ${Q1:.2f}, Q3: ${Q3:.2f}")
print(f"Límites: ${limite_inf:.2f} - ${limite_sup:.2f}")
print(f"Outliers detectados: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

# Mostrar outliers
if len(outliers) > 0:
    print("\nOutliers:")
    print(outliers[['id', 'name', 'precio', 'room_type']].head(10))

# =============================================================================
# 3. VISUALIZACIONES
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Boxplot precios
axes[0,0].boxplot(df['precio']. dropna())
axes[0,0].set_title('Boxplot Precios')
axes[0,0].set_ylabel('Precio ($)')

# Histograma precios (sin outliers extremos)
precio_filtrado = df['precio'][df['precio'] <= limite_sup]
axes[0,1]. hist(precio_filtrado, bins=30, edgecolor='black')
axes[0,1].set_title('Distribución Precios')
axes[0,1].set_xlabel('Precio ($)')

# Distribución de ratings
if 'review_scores_rating' in df.columns:
    df['review_scores_rating'].dropna().hist(ax=axes[1,0], bins=20, edgecolor='black')
    axes[1,0].set_title('Distribución Ratings')
    axes[1,0].set_xlabel('Rating')

# Nulos por columna (top 10)
top_nulos = nulos_df.head(10)
axes[1,1].barh(top_nulos. index, top_nulos['%'])
axes[1,1]. set_title('Top 10 Columnas con Nulos')
axes[1,1].set_xlabel('% Nulos')

plt.tight_layout()
plt.savefig('analisis_airbnb.png', dpi=150)
plt.show()

# =============================================================================
# 4.  RESUMEN RÁPIDO
# =============================================================================

print("\n" + "="*50)
print("RESUMEN")
print("="*50)
print(f"Listings totales: {len(df)}")
print(f"Precio medio: ${df['precio'].mean():.2f}")
print(f"Outliers en precio: {len(outliers)}")
print(f"Listings sin rating: {df['review_scores_rating'].isnull().sum()}")
print(f"Rating medio: {df['review_scores_rating'].mean():.2f}")