import pandas as pd
# import io # Ya no es necesario si cargas el archivo real

# 1. Cargar el CSV real
# Asegúrate de que 'reviews.csv' esté en la misma carpeta o usa la ruta completa
df = pd.read_csv("reviews.csv")

# Opcional: Para verificar los nombres de las columnas que cargó
# print(df.columns)

# La columna de fecha se llama 'date'

# 2. Convertir la columna 'date' a datetime
# Esta línea estaba bien, siempre que la columna exista
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# 3. Encontrar el mínimo y el máximo
fecha_min = df["date"].min()
fecha_max = df["date"].max()

# 4. Resultados
print(f"La fecha más antigua (Mínima) es: {fecha_min}")
print(f"La fecha más reciente (Máxima) es: {fecha_max}")
