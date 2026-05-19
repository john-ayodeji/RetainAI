from typing import Any, Dict, List, Tuple
import json

import joblib
import pandas as pd

from api.services import config


SCALE_COLUMNS = [
    "Age",
    "Tenure",
    "Usage Frequency",
    "Support Calls",
    "Payment Delay",
    "Total Spend",
    "Last Interaction",
    "spend_per_tenure",
    "support_call_rate",
    "usage_per_tenure",
]


def load_feature_names() -> List[str]:
    with open(config.feature_names_path(), "r") as f:
        return json.load(f)


def load_model():
    return joblib.load(config.model_artifact_path())


def load_scaler():
    scaler_path = "ml/artifacts/scaler.pkl"
    return joblib.load(scaler_path)


def build_feature_frame(customer: Dict[str, Any]) -> pd.DataFrame:
    from ml.preprocess import clean_data, engineer_features, encode_features

    df = pd.DataFrame([customer])
    df = clean_data(df)
    df = engineer_features(df)
    df = encode_features(df)
    return df


def prepare_model_frame(customer: Dict[str, Any]) -> Tuple[pd.DataFrame, List[str]]:
    feature_names = load_feature_names()
    df = build_feature_frame(customer)

    try:
        scaler = load_scaler()
        cols_to_scale = [c for c in SCALE_COLUMNS if c in df.columns]
        if cols_to_scale:
            df.loc[:, cols_to_scale] = scaler.transform(df[cols_to_scale])
    except Exception:
        # scaling is best-effort; if scaler is unavailable we still allow inference
        pass

    df = df.reindex(columns=feature_names, fill_value=0)
    return df, feature_names


def predict_churn(customer: Dict[str, Any]) -> Tuple[float, pd.DataFrame, List[str]]:
    model = load_model()
    df, feature_names = prepare_model_frame(customer)
    proba = float(model.predict_proba(df)[0, 1])
    return proba, df, feature_names
