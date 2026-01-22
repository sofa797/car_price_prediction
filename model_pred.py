import numpy as np
import pandas as pd
import joblib
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

def _load_model():
    weights = np.load(os.path.join(MODEL_DIR, 'weights.npy'))
    bias = np.load(os.path.join(MODEL_DIR, 'bias.npy'))
    feature_names = np.load(os.path.join(MODEL_DIR, 'feature_names.npy'), allow_pickle=True)
    full_columns = joblib.load(os.path.join(MODEL_DIR, 'full_columns.pkl'))
    cat_cols = joblib.load(os.path.join(MODEL_DIR, 'cat_cols.pkl'))
    return weights, bias, feature_names, full_columns, cat_cols

try:
    WEIGHTS, BIAS, FEATURE_NAMES, FULL_COLUMNS, CAT_COLS = _load_model()
except FileNotFoundError as e:
    raise RuntimeError(f"files are not found in directory '{MODEL_DIR}'") from e

def predict_car_price(user_data: dict) -> float:
    required_keys = set(CAT_COLS + [
        'symboling', 'wheelbase', 'carlength', 'carwidth', 'carheight',
        'curbweight', 'enginesize', 'boreratio', 'stroke', 'compressionratio',
        'horsepower', 'peakrpm', 'citympg', 'highwaympg'
    ])
    missing = required_keys - set(user_data.keys())
    if missing:
        raise ValueError(f"mandatory fields are absent {missing}")
    
    df_input = pd.DataFrame([user_data])
    df_encoded = pd.get_dummies(df_input, columns=CAT_COLS, drop_first=True)
    X_ready = pd.DataFrame(0, index=[0], columns=FULL_COLUMNS, dtype=float)
    for col in df_encoded.columns:
        if col in X_ready.columns:
            X_ready[col] = df_encoded[col].iloc[0]
    X_final = X_ready[FEATURE_NAMES].values.astype(float)

    price = X_final @ WEIGHTS + BIAS
    predicted_price = float(price[0])

    return max(0.0, predicted_price)