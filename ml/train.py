from preprocess import (
    preprocess_dataset,
    split_data,
    scale_features,
    handle_imbalance,
    select_and_save_features,
)
import os
import joblib
from xgboost import XGBClassifier
import sys
try:
    # when running as a module: `python -m ml.train`
    from ml.evaluate import evaluate_model
except Exception:
    # when running as a script: `python ml/train.py`
    from evaluate import evaluate_model

df = preprocess_dataset()
select_and_save_features(df)
X_train, X_cv, X_test, y_train, y_cv, y_test = split_data(df)
X_train, X_cv, X_test = scale_features(X_train, X_cv, X_test)
X_train_bal, y_train_bal = handle_imbalance(X_train, y_train)

artifacts_dir = os.path.join("ml", "artifacts")
os.makedirs(artifacts_dir, exist_ok=True)
final_model_path = os.path.join(artifacts_dir, "model.pkl")

params = {
    "n_estimators": 300,
    "max_depth": 4,
    "learning_rate": 0.05,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "random_state": 42,
    "n_jobs": -1,
}

# Train model
print("Training XGBoost model with parameters:")
for k, v in params.items():
    print(f"  {k}: {v}")

model = XGBClassifier(**params)
model.fit(X_train_bal, y_train_bal)

# Evaluate and persist
evaluate_model(model, X_test, y_test, name="Final XGBoost")
joblib.dump(model, final_model_path)
print(f"Saved final model to {final_model_path}")