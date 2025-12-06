#!/usr/bin/env python3
"""
Análise Exploratoria de Datos para o dataset de AirBnB
Xera figuras listas para publicación usando o esquema de cores do proxecto
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import rcParams
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Cores personalizadas do LaTeX
AZULITO = '#BAC8D3'      # RGB(186,200,211) - azul claro
AZUL_OSCURO = '#23445D'  # RGB(35,68,93) - azul escuro
TURQUESA = '#AE8FAB'     # RGB(174,143,171) - púrpura

# Configurar gráficos
sns.set_style("whitegrid")
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
rcParams['axes.titleweight'] = 'bold'
rcParams['axes.labelweight'] = 'semibold'
rcParams['figure.titlesize'] = 14
rcParams['figure.titleweight'] = 'bold'

# Rutas
DATA_FILE = "dataset/merged.csv"
FIG_DIR = Path("diagramas")
FIG_DIR.mkdir(exist_ok=True)

def print_section(title):
    """Imprime cabeceiras de sección"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def listings_per_city(df):
    """1. Hospedaxes por cidade"""
    print_section("HOSPEDAXES POR CIDADE")
    
    city_counts = df['city'].value_counts().sort_values(ascending=True)
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(range(len(city_counts)), city_counts.values,
                    color=AZUL_OSCURO, edgecolor='white', linewidth=2)
    
    # Engadir valores nas barras
    for i, (city, count) in enumerate(zip(city_counts.index, city_counts.values)):
        plt.text(count + max(city_counts.values)*0.01, i, f'{count:,}',
                va='center', fontsize=10, fontweight='bold')
    
    plt.yticks(range(len(city_counts)), [c.title() for c in city_counts.index],
              fontsize=11)
    plt.xlabel('Número de Hospedaxes', fontsize=12, fontweight='bold')
    plt.title('Distribución de Hospedaxes por Cidade', fontsize=14, 
             fontweight='bold', color=AZUL_OSCURO, pad=20)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_01_hospedaxes_cidade.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_01_hospedaxes_cidade.png")
    
    print("\nEstadísticas por cidade:")
    for city, count in city_counts.items():
        pct = count / len(df) * 100
        print(f"  {city.title():20s}: {count:6,} ({pct:5.2f}%)")

def price_analysis(df):
    """2. Análise da distribución de prezos"""
    print_section("ANÁLISE DE PREZOS")
    
    # Eliminar outliers extremos para visualización (mantén o 99%)
    price_99 = df['price'].quantile(0.99)
    df_viz = df[df['price'] <= price_99].copy()
    
    print(f"Estadísticas de prezo (dataset completo):")
    print(df['price'].describe())
    print(f"\nOutliers detectados (> percentil 99): {(df['price'] > price_99).sum():,} hospedaxes")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Análise da Distribución de Prezos', fontsize=16, fontweight='bold', color=AZUL_OSCURO)
    
    # 1. Histograma
    axes[0, 0].hist(df_viz['price'], bins=50, color=AZUL_OSCURO, 
                    edgecolor='white', alpha=0.8)
    axes[0, 0].axvline(df['price'].median(), color=TURQUESA, 
                       linestyle='--', linewidth=2, label=f'Mediana: ${df["price"].median():.0f}')
    axes[0, 0].set_xlabel('Prezo ($)', fontsize=11)
    axes[0, 0].set_ylabel('Frecuencia', fontsize=11)
    axes[0, 0].set_title('Distribución de Prezos (percentil 99)', color=AZUL_OSCURO)
    axes[0, 0].legend()
    
    # 2. Prezo vs capacidade
    scatter_data = df_viz.groupby('accommodates').agg({
        'price': ['mean', 'std', 'count']
    }).reset_index()
    scatter_data.columns = ['accommodates', 'mean_price', 'std_price', 'count']
    
    axes[0, 1].scatter(scatter_data['accommodates'], scatter_data['mean_price'],
                       s=scatter_data['count']/10, alpha=0.6, color=AZUL_OSCURO)
    axes[0, 1].set_xlabel('Número de Hóspedes', fontsize=11)
    axes[0, 1].set_ylabel('Prezo Medio ($)', fontsize=11)
    axes[0, 1].set_title('Prezo vs Capacidade (tamaño = conteo)', color=AZUL_OSCURO)
    
    # 3. Distribución en escala logarítmica
    axes[1, 0].hist(np.log10(df[df['price'] > 0]['price']), bins=50, 
                    color=TURQUESA, edgecolor='white', alpha=0.8)
    axes[1, 0].set_xlabel('log₁₀(Prezo)', fontsize=11)
    axes[1, 0].set_ylabel('Frecuencia', fontsize=11)
    axes[1, 0].set_title('Distribución de Prezos (escala log)', color=AZUL_OSCURO)
    
    # 4. Estatísticas por cidade
    city_stats = df.groupby('city')['price'].agg(['mean', 'median', 'std']).sort_values('median', ascending=False)
    x = range(len(city_stats))
    axes[1, 1].bar(x, city_stats['median'], color=AZULITO, 
                   edgecolor=AZUL_OSCURO, linewidth=2, label='Mediana')
    axes[1, 1].errorbar(x, city_stats['mean'], yerr=city_stats['std']/2, 
                       fmt='o', color=TURQUESA, markersize=8, 
                       capsize=5, label='Media ± 0.5*σ', linewidth=2)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels([c.title() for c in city_stats.index], rotation=45, ha='right')
    axes[1, 1].set_ylabel('Prezo ($)', fontsize=11)
    axes[1, 1].set_title('Prezos por Cidade', color=AZUL_OSCURO)
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_02_analise_prezos.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_02_analise_prezos.png")

def price_violin_by_city(df):
    """3. Violin plot de prezos por cidade"""
    print_section("DISTRIBUCIÓN DE PREZOS POR CIDADE (VIOLIN)")
    
    # Limitar ao percentil 95 para mellor visualización
    price_95 = df['price'].quantile(0.95)
    df_viz = df[df['price'] <= price_95].copy()
    
    city_order = df_viz.groupby('city')['price'].median().sort_values(ascending=False).index
    
    plt.figure(figsize=(14, 8))
    
    # Crear violin plot
    parts = plt.violinplot([df_viz[df_viz['city'] == city]['price'].values 
                            for city in city_order],
                           positions=range(len(city_order)),
                           showmeans=True, showmedians=True, widths=0.7)
    
    # Personalizar cores
    for pc in parts['bodies']:
        pc.set_facecolor(AZULITO)
        pc.set_edgecolor(AZUL_OSCURO)
        pc.set_alpha(0.7)
        pc.set_linewidth(2)
    
    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians', 'cmeans'):
        if partname in parts:
            vp = parts[partname]
            vp.set_edgecolor(AZUL_OSCURO)
            vp.set_linewidth(2)
    
    plt.xticks(range(len(city_order)), [c.title() for c in city_order], 
              rotation=45, ha='right', fontsize=11)
    plt.ylabel('Prezo ($)', fontsize=12, fontweight='bold')
    plt.title('Distribución de Prezos por Cidade (Violin Plot)', 
             fontsize=14, fontweight='bold', color=AZUL_OSCURO, pad=20)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_03_prezos_violin.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_03_prezos_violin.png")

def property_characteristics(df):
    """4. Análise das características das propiedades"""
    print_section("CARACTERÍSTICAS DAS PROPIEDADES")
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Características das Propiedades', fontsize=16, fontweight='bold', color=AZUL_OSCURO)
    
    # 1. Distribución de cuartos
    bedroom_counts = df['bedrooms'].value_counts().sort_index().head(10)
    axes[0, 0].bar(bedroom_counts.index, bedroom_counts.values,
                   color=AZUL_OSCURO, edgecolor='white', linewidth=2)
    axes[0, 0].set_xlabel('Número de Cuartos', fontsize=11)
    axes[0, 0].set_ylabel('Conteo', fontsize=11)
    axes[0, 0].set_title('Distribución de Cuartos', color=AZUL_OSCURO)
    
    # 2. Distribución de baños
    bathroom_counts = df['bathrooms'].value_counts().sort_index().head(10)
    axes[0, 1].bar(bathroom_counts.index, bathroom_counts.values,
                   color=AZULITO, edgecolor=AZUL_OSCURO, linewidth=2)
    axes[0, 1].set_xlabel('Número de Baños', fontsize=11)
    axes[0, 1].set_ylabel('Conteo', fontsize=11)
    axes[0, 1].set_title('Distribución de Baños', color=AZUL_OSCURO)
    
    # 3. Distribución de capacidade
    accom_counts = df['accommodates'].value_counts().sort_index().head(15)
    axes[0, 2].bar(accom_counts.index, accom_counts.values,
                   color=TURQUESA, edgecolor='white', linewidth=2)
    axes[0, 2].set_xlabel('Máx. Hóspedes', fontsize=11)
    axes[0, 2].set_ylabel('Conteo', fontsize=11)
    axes[0, 2].set_title('Distribución de Capacidade', color=AZUL_OSCURO)
    
    # 4. Tipos de propiedade (top 10)
    prop_types = df['property_type'].value_counts().head(10)
    axes[1, 0].barh(range(len(prop_types)), prop_types.values,
                    color=AZUL_OSCURO, edgecolor='white', linewidth=2)
    axes[1, 0].set_yticks(range(len(prop_types)))
    axes[1, 0].set_yticklabels([pt[:30] for pt in prop_types.index], fontsize=9)
    axes[1, 0].set_xlabel('Conteo', fontsize=11)
    axes[1, 0].set_title('Top 10 Tipos de Propiedade', color=AZUL_OSCURO)
    axes[1, 0].invert_yaxis()
    
    # 5. Reserva instantánea
    instant_counts = df['instant_bookable'].value_counts()
    axes[1, 1].pie(instant_counts.values, labels=['Non Instantánea', 'Instantánea'],
                   colors=[AZULITO, TURQUESA], autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
    axes[1, 1].set_title('Dispoñibilidade de Reserva Instantánea', color=AZUL_OSCURO)
    
    # 6. Dispoñibilidade
    axes[1, 2].hist(df['availability_eoy'], bins=30, color=AZUL_OSCURO,
                    edgecolor='white', alpha=0.8)
    axes[1, 2].set_xlabel('Días Dispoñibles (Fin de Ano)', fontsize=11)
    axes[1, 2].set_ylabel('Frecuencia', fontsize=11)
    axes[1, 2].set_title('Distribución de Dispoñibilidade', color=AZUL_OSCURO)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_04_caracteristicas_propiedades.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_04_caracteristicas_propiedades.png")

def review_scores_analysis(df):
    """5. Análise de puntuacións de reseñas"""
    print_section("ANÁLISE DE PUNTUACIÓNS")
    
    score_cols = [c for c in df.columns if c.startswith('review_scores_')]
    df_scores = df[score_cols].dropna()
    
    print(f"Reseñas dispoñibles para {len(df_scores):,} / {len(df):,} hospedaxes ({len(df_scores)/len(df)*100:.1f}%)")
    print("\nEstadísticas de puntuacións:")
    print(df_scores.describe())
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Análise de Puntuacións de Reseñas', fontsize=16, fontweight='bold', color=AZUL_OSCURO)
    
    # 1. Distribucións de puntuacións (violin plot)
    score_names = [c.replace('review_scores_', '').replace('_', ' ').title() 
                   for c in score_cols]
    score_data = pd.DataFrame({name: df[col].dropna() for name, col in zip(score_names, score_cols)})
    
    positions = range(len(score_names))
    parts = axes[0, 0].violinplot([score_data[name].values for name in score_names],
                                   positions=positions, showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor(AZULITO)
        pc.set_alpha(0.7)
        pc.set_edgecolor(AZUL_OSCURO)
        pc.set_linewidth(1.5)
    
    axes[0, 0].set_xticks(positions)
    axes[0, 0].set_xticklabels(score_names, rotation=45, ha='right', fontsize=9)
    axes[0, 0].set_ylabel('Puntuación', fontsize=11)
    axes[0, 0].set_title('Distribucións de Puntuacións (Violin)', color=AZUL_OSCURO)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Mapa de correlacións
    corr = df_scores.corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, ax=axes[0, 1], cbar_kws={'label': 'Correlación'})
    axes[0, 1].set_title('Correlacións entre Puntuacións', color=AZUL_OSCURO)
    
    # 3. Puntuacións medias por cidade
    city_scores = df.groupby('city')[score_cols[0]].mean().sort_values(ascending=False)
    axes[1, 0].barh(range(len(city_scores)), city_scores.values,
                    color=TURQUESA, edgecolor='white', linewidth=2)
    axes[1, 0].set_yticks(range(len(city_scores)))
    axes[1, 0].set_yticklabels([c.title() for c in city_scores.index], fontsize=9)
    axes[1, 0].set_xlabel('Puntuación Media', fontsize=11)
    axes[1, 0].set_title('Puntuación Media por Cidade', color=AZUL_OSCURO)
    axes[1, 0].invert_yaxis()
    
    # 4. Distribución do número de reseñas
    axes[1, 1].hist(df[df['number_of_reviews'] > 0]['number_of_reviews'], 
                    bins=50, color=AZUL_OSCURO, edgecolor='white', alpha=0.8)
    axes[1, 1].set_xlabel('Número de Reseñas', fontsize=11)
    axes[1, 1].set_ylabel('Frecuencia', fontsize=11)
    axes[1, 1].set_title('Distribución do Número de Reseñas', color=AZUL_OSCURO)
    axes[1, 1].set_xlim(0, df['number_of_reviews'].quantile(0.95))
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_05_puntuacions.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_05_puntuacions.png")

def host_analysis(df):
    """6. Análise das características dos hospedadores"""
    print_section("ANÁLISE DOS HOSPEDADORES")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Características dos Hospedadores', fontsize=16, fontweight='bold', color=AZUL_OSCURO)
    
    # 1. Distribución de Superhosts
    superhost_counts = df['host_is_superhost'].value_counts()
    axes[0, 0].pie(superhost_counts.values, labels=['Regular', 'Superhost'],
                   colors=[AZULITO, TURQUESA], autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
    axes[0, 0].set_title('Distribución de Superhosts', color=AZUL_OSCURO)
    
    # 2. Número de hospedaxes por host (SEN LÍMITE)
    axes[0, 1].hist(df['host_total_listings_count'], bins=50, color=AZUL_OSCURO,
                    edgecolor='white', alpha=0.8, range=(0, df['host_total_listings_count'].quantile(0.95)))
    axes[0, 1].set_xlabel('Número de Hospedaxes por Host', fontsize=11)
    axes[0, 1].set_ylabel('Frecuencia', fontsize=11)
    axes[0, 1].set_title('Distribución de Hospedaxes por Host (percentil 95)', color=AZUL_OSCURO)
    axes[0, 1].axvline(df['host_total_listings_count'].median(), color=TURQUESA,
                      linestyle='--', linewidth=2, label=f'Mediana: {df["host_total_listings_count"].median():.0f}')
    axes[0, 1].legend()
    
    # 3. Tempo de resposta
    response_counts = df['host_response_time'].value_counts().head(6)
    axes[1, 0].barh(range(len(response_counts)), response_counts.values,
                    color=TURQUESA, edgecolor='white', linewidth=2)
    axes[1, 0].set_yticks(range(len(response_counts)))
    axes[1, 0].set_yticklabels(response_counts.index, fontsize=9)
    axes[1, 0].set_xlabel('Conteo', fontsize=11)
    axes[1, 0].set_title('Tempo de Resposta do Host', color=AZUL_OSCURO)
    axes[1, 0].invert_yaxis()
    
    # 4. Estado de verificación
    verif_data = pd.DataFrame({
        'Foto de Perfil': df['host_has_profile_pic'].value_counts(),
        'ID Verificado': df['host_identity_verified'].value_counts()
    })
    verif_data.plot(kind='bar', ax=axes[1, 1], color=[AZULITO, AZUL_OSCURO],
                    edgecolor='white', linewidth=2, rot=0)
    axes[1, 1].set_xlabel('Estado', fontsize=11)
    axes[1, 1].set_xticklabels(['Non', 'Si'], fontsize=11)
    axes[1, 1].set_ylabel('Conteo', fontsize=11)
    axes[1, 1].set_title('Estado de Verificación do Host', color=AZUL_OSCURO)
    axes[1, 1].legend(title='Tipo de Verificación', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_06_hospedadores.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_06_hospedadores.png")
    
    # Estatísticas adicionais
    print(f"\nEstadísticas de hospedaxes por host:")
    print(f"  Media: {df['host_total_listings_count'].mean():.2f}")
    print(f"  Mediana: {df['host_total_listings_count'].median():.2f}")
    print(f"  Máximo: {df['host_total_listings_count'].max():.0f}")
    print(f"  Percentil 95: {df['host_total_listings_count'].quantile(0.95):.0f}")

def geospatial_9_cities(df):
    """7. Mapas de densidade para 9 cidades (3x3)"""
    print_section("DISTRIBUCIÓN XEOGRÁFICA - 9 CIDADES")
    
    # Seleccionar as 9 cidades con máis hospedaxes
    top_cities = df['city'].value_counts().head(9).index.tolist()
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    fig.suptitle('Densidade de Hospedaxes por Cidade', fontsize=18, 
                 fontweight='bold', color=AZUL_OSCURO, y=0.995)
    axes = axes.flatten()
    
    for idx, city in enumerate(top_cities):
        city_df = df[df['city'] == city]
        
        # Limitar ao centro (eliminar outliers xeográficos)
        lon_center = city_df['longitude'].median()
        lat_center = city_df['latitude'].median()
        lon_std = city_df['longitude'].std()
        lat_std = city_df['latitude'].std()
        
        city_filtered = city_df[
            (np.abs(city_df['longitude'] - lon_center) < 3 * lon_std) &
            (np.abs(city_df['latitude'] - lat_center) < 3 * lat_std)
        ]
        
        # Crear hexbin
        hb = axes[idx].hexbin(city_filtered['longitude'], city_filtered['latitude'],
                             gridsize=40, cmap='YlOrRd', alpha=0.8, mincnt=1)
        
        axes[idx].set_xlabel('Lonxitude', fontsize=9)
        axes[idx].set_ylabel('Latitude', fontsize=9)
        axes[idx].set_title(f'{city.title()} (n={len(city_df):,})', 
                           fontsize=11, fontweight='bold', color=AZUL_OSCURO)
        axes[idx].tick_params(labelsize=8)
        
        # Engadir colorbar pequena
        cbar = plt.colorbar(hb, ax=axes[idx], pad=0.02)
        cbar.set_label('Densidade', fontsize=8)
        cbar.ax.tick_params(labelsize=7)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_07_xeografia_9cidades.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_07_xeografia_9cidades.png")

def geospatial_all_cities(df):
    """8. Mapa xeográfico con todas as cidades xuntas"""
    print_section("DISTRIBUCIÓN XEOGRÁFICA - TODAS AS CIDADES")
    
    try:
        import contextily as ctx
        use_basemap = True
        print("✓ Contextily dispoñible - usando mapa satelital")
    except ImportError:
        use_basemap = False
        print("⚠ Contextily non dispoñible - mapa sen fondo satelital")
        print("  Instalar con: pip install contextily")
    
    # Mostrear datos para mellor rendemento
    df_sample = df.sample(min(15000, len(df)), random_state=42)
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    cities = df_sample['city'].unique()
    colors_map = {city: color for city, color in zip(cities, 
                  [AZULITO, AZUL_OSCURO, TURQUESA, '#FF6B6B', '#4ECDC4', 
                   '#45B7D1', '#96CEB4', '#FFEAA7', '#DFE6E9', '#74B9FF',
                   '#A29BFE', '#FD79A8', '#FDCB6E', '#6C5CE7', '#00B894'] * 2)}
    
    # Plotear cada cidade
    for city in cities:
        city_data = df_sample[df_sample['city'] == city]
        ax.scatter(city_data['longitude'], city_data['latitude'],
                  alpha=0.6, s=15, label=city.title(), 
                  color=colors_map.get(city, AZUL_OSCURO),
                  edgecolors='white', linewidth=0.3)
    
    # Engadir mapa base se está dispoñible
    if use_basemap:
        try:
            # Converter a Web Mercator
            import geopandas as gpd
            from shapely.geometry import Point
            
            gdf = gpd.GeoDataFrame(
                df_sample,
                geometry=[Point(xy) for xy in zip(df_sample['longitude'], df_sample['latitude'])],
                crs='EPSG:4326'
            )
            gdf = gdf.to_crs(epsg=3857)
            
            fig, ax = plt.subplots(figsize=(16, 10))
            
            for city in cities:
                city_gdf = gdf[gdf['city'] == city]
                city_gdf.plot(ax=ax, alpha=0.6, markersize=15, 
                            label=city.title(), color=colors_map.get(city, AZUL_OSCURO),
                            edgecolor='white', linewidth=0.3)
            
            ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, alpha=0.5)
            ax.set_xlabel('Lonxitude', fontsize=12, fontweight='bold')
            ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
            
        except Exception as e:
            print(f"⚠ Erro ao engadir mapa base: {e}")
            print("  Usando mapa sen fondo satelital")
            use_basemap = False
    
    if not use_basemap:
        ax.set_xlabel('Lonxitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    ax.set_title('Distribución Xeográfica de Todas as Hospedaxes', 
                fontsize=16, fontweight='bold', color=AZUL_OSCURO, pad=20)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9, 
             framealpha=0.9, edgecolor=AZUL_OSCURO, fancybox=True)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_08_xeografia_todas.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_08_xeografia_todas.png")

def outlier_detection(df):
    """9. Detección de outliers para características numéricas"""
    print_section("DETECCIÓN DE OUTLIERS")
    
    numerical_cols = ['price', 'bedrooms', 'bathrooms', 'accommodates', 
                     'number_of_reviews', 'availability_eoy']
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Detección de Outliers (Box Plots)', fontsize=16, fontweight='bold', color=AZUL_OSCURO)
    axes = axes.flatten()
    
    for idx, col in enumerate(numerical_cols):
        data = df[col].dropna()
        
        # Calcular outliers usando método IQR
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = ((data < lower_bound) | (data > upper_bound)).sum()
        
        bp = axes[idx].boxplot([data], vert=True, patch_artist=True,
                               boxprops=dict(facecolor=AZULITO, color=AZUL_OSCURO, linewidth=2),
                               medianprops=dict(color=TURQUESA, linewidth=2),
                               whiskerprops=dict(color=AZUL_OSCURO, linewidth=1.5),
                               capprops=dict(color=AZUL_OSCURO, linewidth=1.5),
                               flierprops=dict(marker='o', markerfacecolor=TURQUESA, 
                                             markersize=4, alpha=0.5))
        
        col_name = col.replace('_', ' ').title()
        axes[idx].set_ylabel(col_name, fontsize=11)
        axes[idx].set_title(f'{col_name}\n({outliers:,} outliers, {outliers/len(data)*100:.1f}%)',
                           color=AZUL_OSCURO, fontsize=10, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_09_outliers.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_09_outliers.png")
    
    # Imprimir estatísticas de outliers
    print("\nEstatísticas de Outliers (método IQR):")
    for col in numerical_cols:
        data = df[col].dropna()
        Q1, Q3 = data.quantile([0.25, 0.75])
        IQR = Q3 - Q1
        outliers = ((data < Q1 - 1.5*IQR) | (data > Q3 + 1.5*IQR)).sum()
        print(f"  {col:30s}: {outliers:6,} ({outliers/len(data)*100:5.2f}%)")

def correlation_analysis(df):
    """10. Análise de correlacións entre características numéricas"""
    print_section("ANÁLISE DE CORRELACIÓNS")
    
    numerical_cols = ['price', 'bedrooms', 'bathrooms', 'beds', 'accommodates',
                     'number_of_reviews', 'availability_eoy', 'reviews_per_month',
                     'host_total_listings_count']
    
    corr_matrix = df[numerical_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=2, cbar_kws={'label': 'Coeficiente de Correlación'})
    plt.title('Matriz de Correlacións entre Características', fontsize=16, fontweight='bold', 
              color=AZUL_OSCURO, pad=20)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_10_correlacions.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gardado: eda_10_correlacions.png")
    
    # Imprimir correlacións máis fortes
    print("\nCorrelacións positivas máis fortes (excluíndo diagonal):")
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], 
                             corr_matrix.iloc[i, j]))
    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for var1, var2, corr in corr_pairs[:5]:
        print(f"  {var1:25s} <-> {var2:25s}: {corr:6.3f}")

def main():
    """Executar todas as análises EDA"""
    print("\n" + "="*70)
    print("  ANÁLISE EXPLORATORIA DE DATOS - Dataset AirBnB")
    print("="*70)
    print(f"\nLendo datos de: {DATA_FILE}")
    print(f"Gardando figuras en: {FIG_DIR}/")
    
    # Cargar datos
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"✓ Cargados {len(df):,} filas × {len(df.columns)} columnas")
    
    # Executar análises
    analyses = [
        listings_per_city,
        price_analysis,
        price_violin_by_city,
        property_characteristics,
        review_scores_analysis,
        host_analysis,
        geospatial_9_cities,
        geospatial_all_cities,
        outlier_detection,
        correlation_analysis
    ]
    
    for analysis_func in analyses:
        try:
            analysis_func(df)
        except Exception as e:
            print(f"✗ Erro en {analysis_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print_section("ANÁLISE COMPLETA")
    print(f"Todas as figuras gardadas en: {FIG_DIR}/")
    print("\nFicheiros xerados:")
    for i in range(1, 11):
        print(f"  - eda_{i:02d}_*.png")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
