from typing import Dict, Any, Optional
from typing import List
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


class CustomerRecord(BaseModel):
	data: Dict[str, Any]


class CustomerListResponse(BaseModel):
	page: int
	limit: int
	total: int
	total_pages: int
	previous: Optional[str] = None
	next: Optional[str] = None
	data: List[Dict[str, Any]]


class UserSearchResponse(BaseModel):
	page: int
	limit: int
	total: int
	total_pages: int
	previous: Optional[str] = None
	next: Optional[str] = None
	filters: Dict[str, Any]
	data: List[Dict[str, Any]]
