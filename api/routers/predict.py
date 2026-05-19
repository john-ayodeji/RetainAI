from fastapi import APIRouter, HTTPException
from api.services.schemas import CustomerInput, PredictionOutput
from api.services import config
from api.services import shap_service
import joblib
import pandas as pd

router = APIRouter()


def _to_dataframe(customer: dict, feature_names: list) -> pd.DataFrame:
	df = pd.DataFrame([customer])
	return df[feature_names]


@router.post("/predict", response_model=PredictionOutput)
def predict(payload: CustomerInput):
	# Load model
	model_path = config.model_artifact_path()
	try:
		model = joblib.load(model_path)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")

	# Load feature names to order columns
	import json, os

	feature_path = config.feature_names_path()
	try:
		with open(feature_path, "r") as f:
			feature_names = json.load(f)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to load feature names: {e}")

	# Build DataFrame and predict
	try:
		df = _to_dataframe(payload.features, feature_names)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid customer features: {e}")

	try:
		proba = float(model.predict_proba(df)[0, 1])
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

	# Compute SHAP context
	try:
		shap_context, shap_raw, base_value = shap_service.compute_shap_for_customer(payload.features)
	except Exception:
		shap_context, shap_raw, base_value = None, None, None

	return PredictionOutput(
		churn_probability=proba,
		shap_context=shap_context,
		shap_raw=shap_raw,
		base_value=base_value,
	)
