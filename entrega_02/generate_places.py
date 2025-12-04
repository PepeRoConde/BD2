import pandas as pd
import os
import numpy as np

# --- 1. Definición de Datos Base y Generación ---

# Ciudades base para simulación (Albany es la real)
CITIES = ['Albany', 'Albany', 'Albany', 'Schenectady', 'Troy']
COUNTRIES = ['USA']
STREET_NAMES = [
    'Ten Broeck St', 'Lark St', 'State St', 'Jay St', 'Delaware Ave',
    'Madison Ave', 'Washington Ave', 'Western Ave', 'Central Ave',
    'Broadway', 'Pearl St', 'Clinton Ave', 'Hudson Ave', 'North St',
    'South St', 'Park Ave'
]

# Inicializar listas para datos finales
streets = []
cities = []
countries = []
latitudes = []
longitudes = []

# Generar 50 filas de datos simulados
NUM_ROWS = 1500

for i in range(NUM_ROWS):
    # Elegir calle y ciudad al azar
    street = np.random.choice(STREET_NAMES)
    city = np.random.choice(CITIES)
    country = np.random.choice(COUNTRIES)

    # Generar latitud y longitud ligeramente dispersas alrededor de Albany (42.65, -73.75)
    # Si la ciudad es Albany, los valores son más realistas para NY.
    if city == 'Albany':
        lat = 42.6 + (np.random.rand() * 0.2)  # 42.6 a 42.8
        lon = -73.7 - (np.random.rand() * 0.2) # -73.7 a -73.9
    else:
         # Valores más dispersos para otras ciudades simuladas
        lat = 40 + (np.random.rand() * 5)
        lon = -75 + (np.random.rand() * 5)
    
    # Redondear para simular precisión de BBDD
    lat = round(lat, 6)
    lon = round(lon, 6)

    streets.append(street)
    cities.append(city)
    countries.append(country)
    latitudes.append(lat)
    longitudes.append(lon)

# Construir el DataFrame final
data_final = {
    'STREET': streets,
    'CITY': cities,
    'COUNTRY': countries,
    'LATITUD': latitudes,
    'LONGITUD': longitudes
}

df = pd.DataFrame(data_final)

# --- 3. Generación del CSV ---
output_file = 'datasets/places.csv'

try:
    df.to_csv(output_file, index=False, sep=',')
    print(f"Éxito: Archivo '{output_file}' generado correctamente.")
    print(f"Total de filas generadas: {len(df)}")
    print("Contenido generado (las primeras 5 filas):")
    print(df.head())
    print("\nEste CSV ya se puede usar en el paso 'CSV File Input' del pipeline ETL_LUGAR.hpl.")
except Exception as e:
    print(f"Error al escribir el archivo: {e}")
