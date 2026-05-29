from preprocess import (
    preprocess_dataset,
    split_data,
    scale_features,
    handle_imbalance,
    select_and_save_features,
)
import argparse
import json
import os
import joblib
import pandas as pd
import sys
import numpy as np
try:
    # when running as a module: `python -m ml.train`
    from ml.evaluate import evaluate_model
except Exception:
    # when running as a script: `python ml/train.py`
    from evaluate import evaluate_model

os.makedirs("data", exist_ok=True)

raw_test = pd.read_csv("data/raw.csv").tail(1500)
raw_test.to_csv("data/test.csv", index=False)

parser = argparse.ArgumentParser(description="Train churn model")
parser.add_argument("--drop-payment-delay", action="store_true", help="Drop the Payment Delay feature before training (to test leakage)")
args = parser.parse_args()

df = preprocess_dataset()
if args.drop_payment_delay and 'Payment Delay' in df.columns:
    df = df.drop(columns=['Payment Delay'])

# persist feature list (after any optional drops)
feature_names = select_and_save_features(df)

X_train, X_cv, X_test, y_train, y_cv, y_test = split_data(df)

X_train, X_cv, X_test = scale_features(X_train, X_cv, X_test)
X_train_bal, y_train_bal = handle_imbalance(X_train, y_train)

artifacts_dir = os.path.join("ml", "artifacts")
os.makedirs(artifacts_dir, exist_ok=True)
final_model_path = os.path.join(artifacts_dir, "model.pkl")

params = {
    "n_estimators": 100,
    "max_depth": 3,
    "learning_rate": 0.05,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "reg_alpha": 1.0,
    "reg_lambda": 1.0,
    "random_state": 42,
    "n_jobs": -1,
}

print("Training XGBoost model with parameters:")
for k, v in params.items():
    print(f"  {k}: {v}")

model = XGBClassifier(**params)
model.fit(
    X_train_bal,
    y_train_bal,
    eval_set=[(X_cv, y_cv)],
    early_stopping_rounds=20,
    verbose=True,
)

evaluate_model(model, X_test, y_test, name="Final XGBoost")
joblib.dump(model, final_model_path)
print(f"Saved final model to {final_model_path}")