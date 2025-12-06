#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import rcParams

# Custom colors matching the LaTeX definitions
AZULITO = '#BAC8D3'      # RGB(186,200,211) - light blue
AZUL_OSCURO = '#23445D'  # RGB(35,68,93) - dark blue
TURQUESA = '#AE8FAB'     # RGB(174,143,171) - purple-ish

# Configure Seaborn and Matplotlib
sns.set_style("whitegrid")

# Font settings
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
rcParams['axes.titleweight'] = 'bold'
rcParams['axes.labelweight'] = 'semibold'
rcParams['figure.titlesize'] = 14
rcParams['figure.titleweight'] = 'bold'

# Input dataset
DATA_FILE = "dataset/merged.csv"
FIG_DIR = Path("diagramas")
FIG_DIR.mkdir(exist_ok=True)

# Columns of interest
MODERATE_LOW_NULL_COLS = ["bathrooms", "beds", "bedrooms", "price", "host_acceptance_rate", 
                          "host_response_rate", "host_total_listings_count", "reviews_per_month"]

def load_data():
    return pd.read_csv(DATA_FILE)

def get_review_cols(df):
    return [c for c in df.columns if c.startswith("review_scores_")]

def null_percentage(df, cols):
    null_pct = df[cols].isnull().mean() * 100
    print("Null percentages per column:")
    print(null_pct.sort_values(ascending=False))
    return null_pct

def plot_null_counts(df, cols):
    null_counts = df[cols].isnull().sum().sort_values(ascending=False)
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(null_counts)), null_counts.values, 
                   color=AZUL_OSCURO, edgecolor='white', linewidth=2)
    
    plt.xticks(range(len(null_counts)), null_counts.index, rotation=45, ha='right')
    plt.ylabel("Number of Nulls")
    plt.title("Null Counts per Column", color=AZUL_OSCURO)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "null_counts_per_column.png", dpi=150)
    plt.close()

def plot_null_correlation(df, cols):
    null_df = df[cols].isnull()
    corr = null_df.corr()
    
    plt.figure(figsize=(12, 10))
    
    # Custom colormap
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    
    sns.heatmap(corr, annot=True, fmt='.2f', cmap=cmap, center=0, 
                square=True, linewidths=1, linecolor='white')
    
    plt.title("Correlacion de valores nulos", color=AZUL_OSCURO)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "null_correlation_heatmap.png", dpi=150)
    plt.close()

def main():
    print("Analisis de valores nulos")
    print(f"Cargando datos desde: {DATA_FILE}")
    print(f"Guardando figuras en: {FIG_DIR}")
    
    df = load_data()
    review_cols = get_review_cols(df)
    ALL_COLS = MODERATE_LOW_NULL_COLS + review_cols
    
    null_pct = null_percentage(df, ALL_COLS)
    plot_null_counts(df, ALL_COLS)
    plot_null_correlation(df, ALL_COLS)
    
    print("Analisis completado")

if __name__ == "__main__":
    main()
