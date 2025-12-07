import pandas as pd
import numpy as np

df = pd.read_csv('entrega_02/datasets/listings.csv')

print("="*80)
print("ANÁLISIS DE COLUMNAS DE BARRIO")
print("="*80)

# Analiza las tres columnas
print("\n1. neighbourhood (texto libre):")
print(df['neighbourhood'].value_counts(dropna=False).head(10))
print(f"   Nulos: {df['neighbourhood'].isna().sum()}")

print("\n2. neighbourhood_cleansed (estandarizado):")
print(df['neighbourhood_cleansed'].value_counts(dropna=False).head(10))
print(f"   Nulos: {df['neighbourhood_cleansed'].isna().sum()}")

print("\n3. neighbourhood_group_cleansed (agrupación):")
print(df['neighbourhood_group_cleansed'].value_counts(dropna=False).head(10))
print(f"   Nulos: {df['neighbourhood_group_cleansed'].isna().sum()}")