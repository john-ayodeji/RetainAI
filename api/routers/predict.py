from fastapi import APIRouter, HTTPException
from api.services.schemas import CustomerInput, PredictionOutput
from api.services import shap_service
from api.services.inference_utils import predict_churn

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(payload: CustomerInput):
	try:
		proba, final_df, _ = predict_churn(payload.features)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

	# Compute SHAP context using the final feature vector
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
