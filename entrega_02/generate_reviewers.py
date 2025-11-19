import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib

# Leer CSV original
df_reviews = pd.read_csv('datasets/reviews.csv')

# Crear dataset de valoradores únicos
df_reviewers = df_reviews.groupby('reviewer_id').agg({
    'reviewer_name': 'first',
    'date': ['min', 'max', 'count']
}).reset_index()

df_reviewers.columns = ['reviewer_id', 'reviewer_name', 'fecha_primera_review', 
                         'fecha_ultima_review', 'total_reviews']

# Funciones de generación
def generar_idade(reviewer_id):
    seed = int(hashlib.md5(str(reviewer_id).encode()).hexdigest()[:8], 16)
    np.random.seed(seed)
    edad = int(np.random.normal(35, 12))
    return max(18, min(80, edad))

def inferir_sexo(nombre):
    if pd.isna(nombre):
        return 'D'
    nombre = str(nombre).lower()
    fem = ['maria', 'ana', 'laura', 'carmen', 'sofia', 'elena']
    masc = ['juan', 'pedro', 'carlos', 'jose', 'john', 'david']
    if any(n in nombre for n in fem):
        return 'M'
    elif any(n in nombre for n in masc):
        return 'H'
    return 'D'

# Aplicar transformaciones
df_reviewers['idade'] = df_reviewers['reviewer_id'].apply(generar_idade)
df_reviewers['sexo'] = df_reviewers['reviewer_name'].apply(inferir_sexo)

# Convertir a datetime
df_reviewers['fecha_primera_review'] = pd.to_datetime(df_reviewers['fecha_primera_review'])
df_reviewers['fecha_ultima_review'] = pd.to_datetime(df_reviewers['fecha_ultima_review'])

# Calcular data_nacemento
df_reviewers['data_nacemento'] = df_reviewers.apply(
    lambda row: row['fecha_primera_review'] - timedelta(days=row['idade']*365),
    axis=1
)

# Simular SCD2
df_reviewers['anos_activo'] = (
    df_reviewers['fecha_ultima_review'] - df_reviewers['fecha_primera_review']
).dt.days / 365

df_scd2 = []

for _, row in df_reviewers.iterrows():
    version_inicial = {
        'reviewer_id': int(row['reviewer_id']),
        'reviewer_name': str(row['reviewer_name']),
        'idade': int(row['idade']),
        'sexo': row['sexo'],
        'data_nacemento': row['data_nacemento'],
        'data_empezou_valer': row['fecha_primera_review'],
        'data_deixou_valer': pd.NaT,  # ← Usar pd.NaT
        'actual': 1
    }
    
    if row['anos_activo'] > 2:
        fecha_cambio = row['fecha_primera_review'] + (
            row['fecha_ultima_review'] - row['fecha_primera_review']
        ) / 2
        
        # Versión histórica
        version_historica = version_inicial.copy()
        version_historica['data_deixou_valer'] = fecha_cambio
        version_historica['actual'] = 0
        df_scd2.append(version_historica)
        
        # Versión actual
        anos_transcurridos = int((row['fecha_ultima_review'] - fecha_cambio).days / 365)
        version_actual = version_inicial.copy()
        version_actual['idade'] = int(row['idade'] + anos_transcurridos)
        version_actual['data_empezou_valer'] = fecha_cambio
        df_scd2.append(version_actual)
    else:
        df_scd2.append(version_inicial)

df_final = pd.DataFrame(df_scd2)

# FORMATEAR PARA CSV
df_final['data_empezou_valer'] = pd.to_datetime(df_final['data_empezou_valer']).dt.strftime('%Y-%m-%d %H:%M:%S')
df_final['data_nacemento'] = pd.to_datetime(df_final['data_nacemento']).dt.strftime('%Y-%m-%d')

# CRÍTICO: Manejar NaT correctamente
df_final['data_deixou_valer'] = df_final['data_deixou_valer'].apply(
    lambda x: '' if pd.isna(x) else pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')
)

# Ordenar
df_final = df_final.sort_values(['reviewer_id', 'data_empezou_valer'])

# Exportar
df_final.to_csv('datasets/dim_valorador_scd2.csv', index=False, na_rep='')

print(f"\n Generado: {len(df_final)} registros")
print(f"   Valoradores únicos: {df_final['reviewer_id'].nunique()}")
print(f"   Históricos: {(df_final['actual']==0).sum()}")
print(f"   Actuales: {(df_final['actual']==1).sum()}")


# Verificar CSV
df_check = pd.read_csv('datasets/dim_valorador_scd2.csv')
print("\n🔍 Verificación:")
print(f"Columnas: {df_check.columns.tolist()}")
print(f"Tipos inferidos:\n{df_check.dtypes}")
print(f"\nPrimeras 3 filas:")
print(df_check.head(3))
print(f"\nNulos en data_deixou_valer: {df_check['data_deixou_valer'].isna().sum()}")
print(f"Vacíos en data_deixou_valer: {(df_check['data_deixou_valer']=='').sum()}")