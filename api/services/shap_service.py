from typing import Dict, Any, Tuple
import pandas as pd
from api.services.config import model_artifact_path, feature_names_path

from ml.explain import (
	load_explainer,
	compute_shap_values,
	format_shap_for_prompt,
	explain_customer as explain_customer_pipeline,
)


def _to_dataframe(customer: Dict[str, Any], feature_names: list) -> pd.DataFrame:
	df = pd.DataFrame([customer])
	# Ensure columns are present and in correct order
	return df[feature_names]


def compute_shap_for_customer(customer: Dict[str, Any]) -> Tuple[str, Dict[str, float], float]:
	"""
	Loads explainer, computes SHAP values for a single customer dict.

	Returns: (shap_context_str, shap_raw_dict, base_value)
	"""
	explainer, feature_names = load_explainer(model_path=model_artifact_path(), feature_path=feature_names_path())
	df = _to_dataframe(customer, feature_names)
	shap_vals, base_value = compute_shap_values(explainer, df)
	shap_context = format_shap_for_prompt(shap_vals, feature_names, df)
	shap_raw = dict(zip(feature_names, shap_vals.tolist()))
	return shap_context, shap_raw, float(base_value)


def explain_with_question(customer: Dict[str, Any], churn_probability: float, question: str, customer_meta: Dict[str, Any] = None):
	"""
	Builds the LLM prompt and SHAP context for a question about a customer.
	Returns dict with keys: prompt, shap_context, base_value, shap_raw
	"""
	return explain_customer_pipeline(
		customer_row=pd.DataFrame([customer]),
		churn_probability=churn_probability,
		question=question,
		customer_meta=customer_meta,
		model_path=model_artifact_path(),
		feature_path=feature_names_path(),
	)
