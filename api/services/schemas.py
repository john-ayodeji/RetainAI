from typing import Dict, Any, Optional
from pydantic import BaseModel


class CustomerInput(BaseModel):
	features: Dict[str, Any]


class PredictionOutput(BaseModel):
	churn_probability: float
	shap_context: Optional[str]
	shap_raw: Optional[Dict[str, float]]
	base_value: Optional[float]


class ExplainRequest(BaseModel):
	question: str
	customer: Dict[str, Any]
	customer_meta: Optional[Dict[str, Any]] = None


class ExplainResponse(BaseModel):
	answer: str
	prompt: str
	shap_context: Optional[str]
	shap_raw: Optional[Dict[str, float]]


class SimulateRequest(BaseModel):
	customer: Dict[str, Any]
	modifications: Dict[str, Any]
	question: Optional[str] = None
	customer_meta: Optional[Dict[str, Any]] = None


class SimulateResponse(PredictionOutput):
	answer: Optional[str] = None
	prompt: Optional[str] = None
