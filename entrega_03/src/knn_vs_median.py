#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

DATA_FILE = "dataset/final.csv"

# Columns to test (moderate-null, non-review_scores)
TEST_COLS = ["bathrooms", "beds", "host_total_listings_count", "bedrooms"]

def load_data():
    df = pd.read_csv(DATA_FILE)
    return df

def kfold_imputation_test(df, col, n_splits=2, knn_neighbors=3):
    """
    Test median vs KNN imputation using K-Fold cross-validation
    Only uses rows with non-null values to simulate "missingness"
    """
    # Only numeric columns for KNN
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != col]

    X = df[numeric_cols].copy()
    y = df[col].copy()

    # Keep only rows where y is not null
    mask = y.notnull()
    X = X[mask]
    y = y[mask]

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    mse_median = []
    mse_knn = []

    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # Introduce artificial missingness in test set
        y_test_missing = y_test.copy()
        missing_mask = np.random.rand(len(y_test)) < 0.2  # simulate 20% missing
        y_test_missing[missing_mask] = np.nan

        # --- Median imputation ---
        median_imp = SimpleImputer(strategy="median")
        median_imp.fit(y_train.values.reshape(-1, 1))
        y_pred_median = median_imp.transform(y_test_missing.values.reshape(-1, 1)).ravel()
        mse_median.append(mean_squared_error(y_test[missing_mask], y_pred_median[missing_mask]))

        # --- KNN imputation ---
        knn_imp = KNNImputer(n_neighbors=knn_neighbors)
        
        # Fit on training set only (include target column)
        X_train_knn_copy = X_train.copy()
        X_train_knn_copy[col] = y_train
        knn_imp.fit(X_train_knn_copy)
        
        # Transform test set (include target column with missing values)
        X_test_knn_copy = X_test.copy()
        X_test_knn_copy[col] = y_test_missing
        y_pred_knn = knn_imp.transform(X_test_knn_copy)[:, -1]
        mse_knn.append(mean_squared_error(y_test[missing_mask], y_pred_knn[missing_mask]))

    return np.mean(mse_median), np.mean(mse_knn)

def main():
    df = load_data()
    for col in TEST_COLS:
        mse_med, mse_knn = kfold_imputation_test(df, col)
        print(f"{col}: Median MSE={mse_med:.4f}, KNN MSE={mse_knn:.4f}")

if __name__ == "__main__":
    main()

