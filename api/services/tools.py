from typing import Any, Dict
import json

from api.services.inference_utils import prepare_model_frame, predict_churn


def _safe_json_parse(text: str):
    try:
        # find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        return json.loads(text[start : end + 1])
    except Exception:
        return None


def run_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches small utility tools used by the LLM.

    Tools:
    - predict: args = {"customer": {...}}
    - simulate: args = {"customer": {...}, "modifications": {...}}
    - shap: args = {"customer": {...}}
    - explain_prompt: args = {"customer": {...}, "churn_probability": 0.3, "question": "..."}

    Returns a dict with keys: success (bool), output (str), data (optional dict)
    """
    if tool_name == "predict":
        # lazy import to avoid heavy deps at import time
        try:
            customer = args.get("customer", {})
            proba, _, _ = predict_churn(customer)
            return {"success": True, "output": f"churn_probability={proba}", "data": {"churn_probability": proba}}
        except Exception as e:
            return {"success": False, "output": f"predict failed: {e}"}

    if tool_name == "simulate":
        try:
            customer = dict(args.get("customer", {}))
            modifications = args.get("modifications", {})
            customer.update(modifications)

            proba, _, _ = predict_churn(customer)
            return {"success": True, "output": f"simulated_churn_probability={proba}", "data": {"churn_probability": proba}}
        except Exception as e:
            return {"success": False, "output": f"simulate failed: {e}"}

    if tool_name == "shap":
        try:
            from api.services import shap_service

            customer = args.get("customer", {})
            shap_context, shap_raw, base_value = shap_service.compute_shap_for_customer(customer)
            return {"success": True, "output": shap_context, "data": {"shap_raw": shap_raw, "base_value": base_value}}
        except Exception as e:
            return {"success": False, "output": f"shap failed: {e}"}

    if tool_name == "explain_prompt":
        try:
            from api.services import shap_service

            customer = args.get("customer", {})
            churn_probability = float(args.get("churn_probability", 0.0))
            question = args.get("question", "Explain this customer")
            customer_meta = args.get("customer_meta", None)
            res = shap_service.explain_with_question(customer, churn_probability, question, customer_meta)
            # return prompt and shap context
            return {"success": True, "output": res.get("prompt"), "data": res}
        except Exception as e:
            return {"success": False, "output": f"explain_prompt failed: {e}"}

    return {"success": False, "output": f"unknown tool: {tool_name}"}

