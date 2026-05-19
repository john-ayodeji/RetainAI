import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)


def _get_proba(model, X):
    """Return probability estimates for the positive class.

    Works for sklearn-style models (predict_proba) and models that return
    direct scores/predictions. Returns a 1d numpy array.
    """
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[:, 1]
    else:
        # fallback: try predict, assume output is probability-like or logits
        proba = np.asarray(model.predict(X)).ravel()
    return proba


def evaluate_model(model, X, y, name="model", threshold=0.5):
    """Evaluate `model` on `(X, y)` and print nicely formatted metrics.

    Returns: dict of metrics.
    """
    proba = _get_proba(model, X)
    pred = (proba >= threshold).astype(int)

    metrics = {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "roc_auc": roc_auc_score(y, proba),
    }

    print("\n" + "=" * 60)
    print(f"Evaluation — {name}")
    print("=" * 60)
    for k, v in metrics.items():
        print(f"{k:10}: {v:.4f}")
    print("\nClassification report:")
    print(classification_report(y, pred, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y, pred))
    print("=" * 60 + "\n")

    return metrics


# def compare_models(results):
#     return None
