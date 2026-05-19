from fastapi import APIRouter, HTTPException
from api.services.schemas import SimulateRequest, PredictionOutput
from api.services import config, shap_service
import joblib
import pandas as pd

router = APIRouter()


@router.post("/simulate", response_model=PredictionOutput)
def simulate(req: SimulateRequest):
	# Merge modifications into customer
	customer = dict(req.customer)
	customer.update(req.modifications)

	# Load model and feature names
	try:
		model = joblib.load(config.model_artifact_path())
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")

	import json

	try:
		with open(config.feature_names_path(), "r") as f:
			feature_names = json.load(f)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to load feature names: {e}")

	try:
		df = pd.DataFrame([customer])[feature_names]
		proba = float(model.predict_proba(df)[0, 1])
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Simulation failed: {e}")

	try:
		shap_context, shap_raw, base_value = shap_service.compute_shap_for_customer(customer)
	except Exception:
		shap_context, shap_raw, base_value = None, None, None

	return PredictionOutput(
		churn_probability=proba,
		shap_context=shap_context,
		shap_raw=shap_raw,
		base_value=base_value,
	)
