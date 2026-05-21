# routers/explain.py
from fastapi import APIRouter, HTTPException
from api.services.schemas import ExplainRequest, ExplainResponse
from api.services import llm_service
from api.services.inference_utils import predict_churn
from ml.explain import explain_customer

router = APIRouter()


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    try:
        churn_probability, df, _ = predict_churn(req.customer)
        result = explain_customer(
            customer_row=df,
            churn_probability=churn_probability,
            question=req.question,
            customer_meta=req.customer_meta,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build explanation: {e}")

    try:
        answer = llm_service.call_llm(result["prompt"])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    return ExplainResponse(
        answer=answer,
        prompt=result["prompt"],
        shap_context=result["shap_context"],
        shap_raw=result["shap_raw"],
        churn_probability=churn_probability,
    )