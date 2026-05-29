# ml/explain.py
import shap
import joblib
import json
import numpy as np
import pandas as pd

def load_explainer(
    model_path="ml/artifacts/model.pkl",
    feature_path="ml/artifacts/feature_names.json"
):
    """
    Loads the trained XGBoost model and wraps it in a SHAP TreeExplainer.
    TreeExplainer is the correct explainer for XGBoost — fast and exact.
    Returns the explainer and feature names list.
    """
    model = joblib.load(model_path)

    with open(feature_path, "r") as f:
        feature_names = json.load(f)

    explainer = shap.TreeExplainer(model)

    return explainer, feature_names


def compute_shap_values(explainer, customer_row: pd.DataFrame):
    """
    Computes SHAP values for a single customer row.
    customer_row must be a DataFrame with the exact 21 features in order.

    Returns:
        shap_vals   — array of shape (21,), one value per feature
        base_value  — the model's average prediction (baseline)
    """
    shap_values = explainer(customer_row)

    # shap_values.values shape: (1, 21) —take the first (only) row
    shap_vals = shap_values.values[0]
    base_value = shap_values.base_values[0]

    return shap_vals, base_value

FEATURE_LABELS = {
    "Age":                 "Customer age",
    "Gender":              "Gender (0=Male, 1=Female)",
    "Tenure":              "Months with the company",
    "Usage Frequency":     "Product usage frequency (times/month)",
    "Support Calls":       "Number of support calls made",
    "Payment Delay":       "Days payments are delayed",
    "Total Spend":         "Total amount spent ($)",
    "Last Interaction":    "Days since last interaction",
    "spend_per_tenure":    "Spend relative to tenure length",
    "support_call_rate":   "Support call rate relative to tenure",
    "usage_per_tenure":    "Usage rate relative to tenure",
    "is_dormant":          "Dormant customer flag (1=no activity in 30+ days)",
    "has_payment_issues":  "Payment issues flag (1=delayed payments exist)",
    "spend_tier":          "Spend tier (0=Low, 1=Medium, 2=High)",
    "age_group":           "Age group (0=Young, 1=Adult, 2=Middle, 3=Senior)",
    "sub_Basic":           "Subscription: Basic plan",
    "sub_Premium":         "Subscription: Premium plan",
    "sub_Standard":        "Subscription: Standard plan",
    "contract_Annual":     "Contract: Annual",
    "contract_Monthly":    "Contract: Monthly",
    "contract_Quarterly":  "Contract: Quarterly",
}


def format_shap_for_prompt(
    shap_vals: np.ndarray,
    feature_names: list,
    customer_row: pd.DataFrame,
    top_n: int = 6
) -> str:
    """
    Converts raw SHAP values into a structured string block
    ready to be injected into an LLM prompt.

    Only returns the top N most influential features (by absolute SHAP value).
    Each line includes: readable label, actual customer value, and direction + magnitude.

    Example output:
        - Days since last interaction: 52 days → increases churn risk by 28.4%
        - Number of support calls made: 8 calls → increases churn risk by 21.1%
        - Months with the company: 3 months → increases churn risk by 15.3%
        - Total amount spent ($): $145.00 → decreases churn risk by 9.2%
    """
    contributions = []
    for feature, shap_val, in zip(feature_names, shap_vals):
        actual_value = customer_row[feature].values[0]
        label = FEATURE_LABELS.get(feature, feature)
        contributions.append({
            "feature":      feature,
            "label":        label,
            "shap_value":   shap_val,
            "actual_value": actual_value,
            "abs_shap":     abs(shap_val),
        })

    # Sort by absolute SHAP value — most influential first
    contributions.sort(key=lambda x: x["abs_shap"], reverse=True)
    top_factors = contributions[:top_n]

    lines = []
    for c in top_factors:
        direction = "increases" if c["shap_value"] > 0 else "decreases"
        magnitude = c["abs_shap"] * 100  # convert to percentage-like scale

        # Format actual value sensibly
        val = c["actual_value"]
        feature = c["feature"]

        if feature == "Total Spend":
            val_str = f"${val:.2f}"
        elif feature in ("is_dormant", "has_payment_issues", "sub_Basic",
                         "sub_Premium", "sub_Standard", "contract_Annual",
                         "contract_Monthly", "contract_Quarterly"):
            val_str = "Yes" if val == 1 else "No"
        elif feature == "Gender":
            val_str = "Female" if val == 1 else "Male"
        elif feature == "spend_tier":
            val_str = {0: "Low", 1: "Medium", 2: "High"}.get(int(val), str(val))
        elif feature == "age_group":
            val_str = {0: "Young (≤25)", 1: "Adult (26–40)",
                       2: "Middle-aged (41–60)", 3: "Senior (60+)"}.get(int(val), str(val))
        elif isinstance(val, float):
            val_str = f"{val:.2f}"
        else:
            val_str = str(int(val))

        lines.append(
            f"- {c['label']}: {val_str} "
            f"→ {direction} churn risk by {magnitude:.1f}pts"
        )

    return "\n".join(lines)

def build_llm_prompt(
    churn_probability: float,
    shap_context: str,
    question: str,
    customer_meta: dict = None
) -> str:
    """
    Assembles the full prompt that goes to the LLM.

    churn_probability   — float between 0 and 1, from the model
    shap_context        — formatted string from format_shap_for_prompt()
    question            — the user's actual question
    customer_meta       — optional dict with readable fields (name, plan, etc.)
                          for extra context in the prompt header
    """
    risk_level = (
        "HIGH"   if churn_probability >= 0.70 else
        "MEDIUM" if churn_probability >= 0.40 else
        "LOW"
    )

    meta_block = ""
    if customer_meta:
        meta_lines = [f"  {k}: {v}" for k, v in customer_meta.items()]
        meta_block = "Customer profile:\n" + "\n".join(meta_lines) + "\n\n"

    prompt = f"""You are a senior customer retention analyst at a SaaS company.
A machine learning model has assessed a customer and produced the following results.

{meta_block}Churn Probability : {churn_probability:.0%}
Risk Level        : {risk_level}

Top factors driving this prediction:
{shap_context}

Rules you must follow:
- Answer only based on the data provided above. Do not make up facts.
- Be specific — reference actual values from the data, not generic advice.
- Be concise. 3–5 sentences maximum unless a longer answer is genuinely needed.
- where needed return estimate new churn risk in response to proposed retention actions, based on the SHAP values and your knowledge of how they interact.
- If the question asks for a retention action, tie it directly to the top risk factors.
- Do not repeat the churn probability or risk level back in your answer unless asked.

Question: {question}
"""
    return prompt

def explain_customer(
    customer_row: pd.DataFrame,
    churn_probability: float,
    question: str,
    customer_meta: dict = None,
    top_n: int = 6,
    model_path: str = "ml/artifacts/model.pkl",
    feature_path: str = "ml/artifacts/feature_names.json"
) -> dict:
    """
    Full pipeline from customer data → LLM-ready prompt.
    Called by the API — returns both the formatted prompt
    and the raw SHAP context so the frontend can render the bar chart too.

    Returns:
        {
            "prompt":       str,   ← send this to the LLM
            "shap_context": str,   ← use this for the SHAP chart in the UI
            "base_value":   float, ← model baseline (useful for waterfall charts)
            "shap_raw":     dict,  ← feature → shap value, for custom frontend rendering
        }
    """
    explainer, feature_names = load_explainer(model_path, feature_path)

    shap_vals, base_value = compute_shap_values(explainer, customer_row)

    shap_context = format_shap_for_prompt(
        shap_vals, feature_names, customer_row, top_n=top_n
    )

    prompt = build_llm_prompt(
        churn_probability=churn_probability,
        shap_context=shap_context,
        question=question,
        customer_meta=customer_meta
    )

    shap_raw = dict(zip(feature_names, shap_vals.tolist()))

    return {
        "prompt":       prompt,
        "shap_context": shap_context,
        "base_value":   float(base_value),
        "shap_raw":     shap_raw,
    }