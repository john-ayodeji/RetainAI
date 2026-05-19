from fastapi import APIRouter, HTTPException
from api.services.schemas import ExplainRequest, ExplainResponse
from api.services import shap_service, llm_service

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
	# Build prompt and shap context
	try:
		result = shap_service.explain_with_question(
			customer=req.customer,
			churn_probability=0.0 if req.customer is None else req.customer.get("churn_probability", 0.0),
			question=req.question,
			customer_meta=req.customer_meta,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to build explanation: {e}")

	prompt = result.get("prompt")
	shap_context = result.get("shap_context")
	shap_raw = result.get("shap_raw")

	# Call LLM
	answer = llm_service.call_llm(prompt)

	return ExplainResponse(answer=answer, prompt=prompt, shap_context=shap_context, shap_raw=shap_raw)
