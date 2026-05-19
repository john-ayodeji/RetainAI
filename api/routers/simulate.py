from fastapi import APIRouter, HTTPException
from api.services.schemas import SimulateRequest, SimulateResponse
from api.services import shap_service, llm_service
from api.services.inference_utils import predict_churn
from ml.explain import build_llm_prompt

router = APIRouter()


@router.post("/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest):
	# Merge modifications into customer
	customer = dict(req.customer)
	customer.update(req.modifications)

	try:
		proba, _, _ = predict_churn(customer)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Simulation failed: {e}")

	try:
		shap_context, shap_raw, base_value = shap_service.compute_shap_for_customer(customer)
	except Exception:
		shap_context, shap_raw, base_value = None, None, None

	question = req.question or (
		"Given this simulated customer profile, explain how the changes affect churn risk and what retention action you recommend."
	)
	answer = None
	prompt = None
	try:
		prompt = build_llm_prompt(
			churn_probability=proba,
			shap_context=shap_context or "",
			question=question,
			customer_meta=req.customer_meta,
		)
		answer = llm_service.call_llm(prompt)
	except Exception:
		answer = None

	return SimulateResponse(
		churn_probability=proba,
		shap_context=shap_context,
		shap_raw=shap_raw,
		base_value=base_value,
		answer=answer,
		prompt=prompt,
	)
