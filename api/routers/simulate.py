from fastapi import APIRouter, HTTPException
from api.services.schemas import SimulateRequest, SimulateResponse
from api.services import llm_service
from api.services.inference_utils import predict_churn
from ml.explain import explain_customer

router = APIRouter()


@router.post("/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest):
    # Apply modifications to the customer profile
    customer = {**req.customer, **req.modifications}

    try:
        proba, df, _ = predict_churn(customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation failed: {e}")

    question = req.question or (
        "Given this simulated customer profile, explain how the changes affect "
        "churn risk and what retention action you recommend."
    )

    try:
        result = explain_customer(
            customer_row=df,
            churn_probability=proba,
            question=question,
            customer_meta=req.customer_meta,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build explanation: {e}")

    try:
        answer = llm_service.call_llm(result["prompt"])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    return SimulateResponse(
        churn_probability=proba,
        shap_context=result["shap_context"],
        shap_raw=result["shap_raw"],
        base_value=result["base_value"],
        answer=answer,
        prompt=result["prompt"],
    )