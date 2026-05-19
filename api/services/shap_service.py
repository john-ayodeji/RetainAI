from typing import Dict, Any, Tuple
import pandas as pd

from ml.explain import (
	load_explainer,
	compute_shap_values,
	format_shap_for_prompt,
)

from api.services.inference_utils import prepare_model_frame


def compute_shap_for_customer(customer: Dict[str, Any]) -> Tuple[str, Dict[str, float], float]:
	"""
	Loads explainer, computes SHAP values for a single customer dict.

	Returns: (shap_context_str, shap_raw_dict, base_value)
	"""
	explainer, feature_names = load_explainer()
	df, _ = prepare_model_frame(customer)
	shap_vals, base_value = compute_shap_values(explainer, df)
	shap_context = format_shap_for_prompt(shap_vals, feature_names, df)
	shap_raw = dict(zip(feature_names, shap_vals.tolist()))
	return shap_context, shap_raw, float(base_value)


def explain_with_question(customer: Dict[str, Any], churn_probability: float, question: str, customer_meta: Dict[str, Any] = None):
	"""
	Builds the LLM prompt and SHAP context for a question about a customer.
	Returns dict with keys: prompt, shap_context, base_value, shap_raw
	"""
	shap_context, shap_raw, base_value = compute_shap_for_customer(customer)
	prompt = f"Customer question: {question}\nChurn probability: {churn_probability:.0%}\n\nTop SHAP factors:\n{shap_context}"
	return {
		"prompt": prompt,
		"shap_context": shap_context,
		"base_value": base_value,
		"shap_raw": shap_raw,
	}
