from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request

from api.services.schemas import CustomerListResponse, CustomerRecord

router = APIRouter()

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "test.csv"


@lru_cache(maxsize=1)
def load_customers_frame() -> pd.DataFrame:
	if not DATA_FILE.exists():
		raise FileNotFoundError(f"Processed CSV not found: {DATA_FILE}")

	return pd.read_csv(DATA_FILE)


@router.get("/customers", response_model=CustomerListResponse)
def list_customers(
	request: Request,
	page: int = Query(1, ge=1, description="1-based page number"),
	limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
):
	try:
		customers = load_customers_frame()
	except FileNotFoundError as exc:
		raise HTTPException(status_code=500, detail=str(exc))
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to load customers: {exc}")

	total = len(customers)
	total_pages = max((total + limit - 1) // limit, 1)
	offset = (page - 1) * limit
	page_rows = customers.iloc[offset:offset + limit]
	# remove churn from returned data
	page_rows = page_rows.drop(columns=["Churn"], errors="ignore")
	previous_link = str(request.url.include_query_params(page=page - 1, limit=limit)) if page > 1 else None
	next_link = str(request.url.include_query_params(page=page + 1, limit=limit)) if page < total_pages else None

	return CustomerListResponse(
		page=page,
		limit=limit,
		total=total,
		total_pages=total_pages,
		previous=previous_link,
		next=next_link,
		data=page_rows.to_dict(orient="records"),
	)


@router.get("/customers/{customer_id}", response_model=CustomerRecord)
def get_customer(customer_id: str):
	"""Return a single customer record by numeric id or email (raw or encoded)."""
	try:
		customers = load_customers_frame()
	except FileNotFoundError as exc:
		raise HTTPException(status_code=500, detail=str(exc))
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to load customers: {exc}")

	# work with list of dicts for flexible matching
	records = customers.to_dict(orient="records")

	def matches(rec: dict) -> bool:
		if rec is None:
			return False
		# normalize keys to lowercase for flexible matching
		low = {k.lower(): v for k, v in (rec.items() if isinstance(rec, dict) else [])}
		# common id field variants
		for key in ("id", "customerid", "customer_id", "customer_id", "customerid"):
			if key in low and low[key] is not None and str(low[key]) == str(customer_id):
				return True
		# email matches (raw)
		email = str(low.get("email") or low.get("e_mail") or "")
		if email and (email == customer_id):
			return True
		# also accept url-encoded email (incoming param may be encoded or decoded)
		try:
			from urllib.parse import quote, unquote
			if email and (quote(email) == customer_id or unquote(customer_id) == email):
				return True
		except Exception:
			pass
		return False

	for r in records:
		if matches(r):
			# remove churn from returned record if present
			r.pop("Churn", None)
			r.pop("churn", None)
			return CustomerRecord(data=r)

	raise HTTPException(status_code=404, detail="Customer not found")
