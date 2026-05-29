from typing import Any, Dict
import json

from api.services.inference_utils import predict_churn


def _safe_json_parse(text: str):
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        return json.loads(text[start: end + 1])
    except Exception:
        return None


def run_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "predict":
        try:
            proba, _, _ = predict_churn(args.get("customer", {}))
            return {"success": True, "output": f"churn_probability={proba}", "data": {"churn_probability": proba}}
        except Exception as e:
            return {"success": False, "output": f"predict failed: {e}"}

    if tool_name == "simulate":
        try:
            customer = {**args.get("customer", {}), **args.get("modifications", {})}
            proba, _, _ = predict_churn(customer)
            return {"success": True, "output": f"simulated_churn_probability={proba}", "data": {"churn_probability": proba}}
        except Exception as e:
            return {"success": False, "output": f"simulate failed: {e}"}

    if tool_name == "shap":
        try:
            from ml.explain import explain_customer
            customer = args.get("customer", {})
            proba, df, _ = predict_churn(customer)
            result = explain_customer(customer_row=df, churn_probability=proba, question="")
            return {"success": True, "output": result["shap_context"], "data": {"shap_raw": result["shap_raw"], "base_value": result["base_value"]}}
        except Exception as e:
            return {"success": False, "output": f"shap failed: {e}"}

    if tool_name == "explain_prompt":
        try:
            from ml.explain import explain_customer
            customer = args.get("customer", {})
            proba, df, _ = predict_churn(customer)
            result = explain_customer(
                customer_row=df,
                churn_probability=float(args.get("churn_probability", proba)),
                question=args.get("question", "Explain this customer"),
                customer_meta=args.get("customer_meta"),
            )
            return {"success": True, "output": result["prompt"], "data": result}
        except Exception as e:
            return {"success": False, "output": f"explain_prompt failed: {e}"}

    return {"success": False, "output": f"unknown tool: {tool_name}"}