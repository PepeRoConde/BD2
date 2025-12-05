#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Input dataset
DATA_FILE = "dataset/final.csv"
FIG_DIR = Path("diagramas")
FIG_DIR.mkdir(exist_ok=True)

# Columns of interest (moderate + low nulls + review_scores)
MODERATE_LOW_NULL_COLS = ["bathrooms", "beds", "bedrooms", "host_total_listings_count"]
REVIEW_SCORE_COLS = [c for c in pd.read_csv(DATA_FILE, nrows=0).columns if c.startswith("review_scores_")]
ALL_COLS = MODERATE_LOW_NULL_COLS + REVIEW_SCORE_COLS

def load_data():
    df = pd.read_csv(DATA_FILE)
    return df

def null_percentage(df, cols):
    null_pct = df[cols].isnull().mean() * 100
    print("Null percentages per column:")
    print(null_pct.sort_values(ascending=False))
    return null_pct

def plot_null_counts(df, cols):
    null_counts = df[cols].isnull().sum().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=null_counts.index, y=null_counts.values)
    plt.xticks(rotation=45)
    plt.ylabel("Number of Nulls")
    plt.title("Null Counts per Column")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "null_counts_per_column.png")
    plt.close()

def plot_null_correlation(df, cols):
    null_df = df[cols].isnull()
    corr = null_df.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0)
    plt.title("Correlacion de valores nulos")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "null_correlation_heatmap.png")
    plt.close()

def plot_null_pairplot(df, cols):
    # Only do pairplot if <= 10 columns (otherwise too busy)
    if len(cols) <= 10:
        null_df = df[cols].isnull().astype(int)
        pairplot = sns.pairplot(null_df)
        pairplot.fig.suptitle("Pairplot of Null Indicators", y=1.02)
        pairplot.fig.tight_layout()
        pairplot.savefig(FIG_DIR / "null_pairplot.png")
        plt.close()

def main():
    df = load_data()
    null_percentage(df, ALL_COLS)
    plot_null_counts(df, ALL_COLS)
    plot_null_correlation(df, ALL_COLS)
    plot_null_pairplot(df, MODERATE_LOW_NULL_COLS)  # smaller set for readability

if __name__ == "__main__":
    main()

