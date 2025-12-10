import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import time

# Carga dos datos
df = pd.read_csv('dataset/merged.csv')

# Limpeza e creación da variable obxectivo
if df['price'].dtype == 'object':
    df['price'] = df['price'].str.replace('$', '', regex=False)
    df['price'] = df['price'].str.replace(',', '', regex=False)
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df.dropna(subset=['price'])

# Eliminación de columnas textuais non necesarias
cols_texto = ['description' ]
df = df.drop([c for c in cols_texto if c in df.columns], axis=1)

# Conversión de columnas categóricas
cols_categoricas = [
    'host_response_time',
    'property_type',
    'host_location',
    'neighbourhood_cleansed',
    'city'
]
cols_categoricas = [c for c in cols_categoricas if c in df.columns]
df = pd.get_dummies(df, columns=cols_categoricas, drop_first=True, dtype=int)

# Conversión de columnas booleanas
cols_bool = ["host_is_superhost", "host_has_profile_pic",
             "host_identity_verified", "instant_bookable"]

for col in cols_bool:
    if col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].map({'t': 1, 'f': 0, 'True': 1, 'False': 0}).fillna(0).astype(int)
        elif df[col].dtype == 'bool':
            df[col] = df[col].astype(int)

# Conversión de porcentaxes
cols_pct = ['host_response_rate', 'host_acceptance_rate']
for col in cols_pct:
    if col in df.columns and df[col].dtype == 'object':
        df[col] = df[col].str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce') / 100

# Conversión de datas
if 'host_since' in df.columns:
    df['host_since'] = pd.to_datetime(df['host_since'], errors='coerce')
    df['host_experience_days'] = (pd.Timestamp.now() - df['host_since']).dt.days
    df = df.drop('host_since', axis=1)

# Amenidades simplificadas
if 'amenities' in df.columns:
    df['amenities_count'] = df['amenities'].apply(
        lambda x: len(str(x).split(',')) if pd.notna(x) else 0
    )
    df = df.drop('amenities', axis=1)

# Imputación de valores numéricos
#for col in df.select_dtypes(include=[np.number]).columns:
#    if df[col].isnull().any():
#        df[col] = df[col].fillna(df[col].median())
#

inicio_imp = time.time()

num_cols = df.select_dtypes(include=[np.number]).columns
imputer = KNNImputer(n_neighbors=5)
df[num_cols] = imputer.fit_transform(df[num_cols])

print(f'Lista imputacion, tardo {time.time() - inicio_imp} segundos')




# Preparación do conxunto de datos
X = df.drop('price', axis=1)
y = df['price']

object_cols = X.select_dtypes(include=['object']).columns
X = X.drop(object_cols, axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modelo XGBoost
print('Empieza a entrenar')
inicio = time.time()
model = XGBRegressor(
    n_estimators=1000,
    learning_rate=0.01,
    max_depth=10,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    tree_method="hist"
)
model.fit(X_train, y_train)
print(f'Acabó de entrenar, le llevó {time.time() - inicio:.2f} segundos')

# Avaliación
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
prezo_medio = y.mean()

# Táboa de métricas
metrics_df = pd.DataFrame({
    "Métrica": [
        "MAE",
        "RMSE",
        "R²",
        "MAPE (\\%)",
        "Prezo medio",
        "MAE / Prezo medio (\\%)"
    ],
    "Valor": [
        f"{mae:.2f}",
        f"{rmse:.2f}",
        f"{r2:.2f}",
        f"{mape:.2f}",
        f"{prezo_medio:.2f}",
        f"{(mae / prezo_medio * 100):.2f}"
    ]
})


resultados_df = pd.DataFrame({
    'Prezo real': y_test.values[:10],
    'Prezo predicido': y_pred[:10],
    'Diferenza': y_test.values[:10] - y_pred[:10],
    'Erro (\\%)': (np.abs(y_test.values[:10] - y_pred[:10]) / y_test.values[:10]) * 100
})

# Round to 2 decimals for LaTeX
resultados_df = resultados_df.round(2)


importances = model.feature_importances_
importance_df = pd.DataFrame({
    'Variable': X.columns,
    'Importancia': importances
}).sort_values('Importancia', ascending=False).head(15)


joblib.dump(model, 'params/airbnb_price_model.pkl')
joblib.dump(list(X.columns), 'feature_columns.pkl')


TABLE_DIR = "tablas/"
os.makedirs(TABLE_DIR, exist_ok=True)

with open(TABLE_DIR + "metricas_modelo.tex", "w") as f:
    f.write(metrics_df.to_latex(index=False, caption="Métricas do modelo", 
                                label="tab:metricas_modelo", escape=True))

with open(TABLE_DIR + "predicions_exemplo.tex", "w") as f:
    f.write(resultados_df.to_latex(index=False, caption="Predicións de exemplo", 
                                   label="tab:predicions_exemplo", escape=True))

with open(TABLE_DIR + "importancia_variables.tex", "w") as f:
    f.write(importance_df.to_latex(index=False, caption="Importancia das variables", 
                                   label="tab:importancia_variables", escape=True))
