from fastapi import APIRouter, HTTPException
from api.services.schemas import CustomerInput, PredictionOutput
from api.services.inference_utils import predict_churn
from ml.explain import explain_customer

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(payload: CustomerInput):
    try:
        proba, df, _ = predict_churn(payload.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    try:
        result = explain_customer(
            customer_row=df,
            churn_probability=proba,
            question="",  # not needed for predict endpoint
        )
        shap_context = result["shap_context"]
        shap_raw = result["shap_raw"]
        base_value = result["base_value"]
    except Exception:
        shap_context, shap_raw, base_value = None, None, None

    return PredictionOutput(
        churn_probability=proba,
        shap_context=shap_context,
        shap_raw=shap_raw,
        base_value=base_value,
    )