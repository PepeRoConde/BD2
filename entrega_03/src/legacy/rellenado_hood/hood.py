import pandas as pd
import seaborn as sb 
import folium
from folium.plugins import HeatMap, MarkerCluster
import matplotlib.pyplot as plt
# Cargar el CSV
df = pd.read_csv('entrega_02/datasets/listings.csv')



# Calcular centro del mapa
centro_lat = df['latitude'].mean()
centro_lon = df['longitude'].mean()

# Crear mapa base
m = folium.Map(location=[centro_lat, centro_lon], 
               zoom_start=12, 
               tiles='OpenStreetMap')

# Opción A: Todos los puntos con MarkerCluster (para muchos puntos)
marker_cluster = MarkerCluster().add_to(m)

# Mostrar solo una muestra si hay muchos datos
muestra = df.sample(min(1000, len(df)))  # Máximo 1000 puntos para mejor rendimiento

for idx, row in muestra.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"ID: {row.get('id', 'N/A')}"
    ).add_to(marker_cluster)

# Opción B: Heatmap
datos_heatmap = [[row['latitude'], row['longitude']] for idx, row in df.iterrows()]
HeatMap(datos_heatmap, radius=10, blur=15, max_zoom=1).add_to(m)

# Guardar mapa
m.save('mapa_listings.html')
print("Mapa guardado como 'mapa_listings.html' - Ábrelo en tu navegador")