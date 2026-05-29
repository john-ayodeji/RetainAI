from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request

from api.services.schemas import UserSearchResponse

router = APIRouter(prefix="/filter", tags=["filter"])

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "test.csv"


@lru_cache(maxsize=1)
def load_users_frame() -> pd.DataFrame:
	if not DATA_FILE.exists():
		raise FileNotFoundError(f"Raw CSV not found: {DATA_FILE}")

	return pd.read_csv(DATA_FILE)


def _normalize_gender(value: Optional[str]) -> Optional[str]:
	if value is None:
		return None

	normalized = value.strip().lower()
	if normalized in {"m", "male"}:
		return "Male"
	if normalized in {"f", "female"}:
		return "Female"
	return value.strip().title()


def _normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().lower()


@router.get("/users", response_model=UserSearchResponse)
def search_users(
	request: Request,
	gender: Optional[str] = Query(None, description="Filter by gender, e.g. m or female"),
	contract: Optional[str] = Query(None, description="Filter by contract length"),
	subscription: Optional[str] = Query(None, description="Filter by subscription type"),
	churn: Optional[int] = Query(None, ge=0, le=1, description="Filter by churn label"),
	page: int = Query(1, ge=1, description="1-based page number"),
	limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
):
	try:
		users = load_users_frame()
	except FileNotFoundError as exc:
		raise HTTPException(status_code=500, detail=str(exc))
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Failed to load users: {exc}")

	filtered = users.copy()
	filters = {}

	gender_value = _normalize_gender(gender)
	if gender_value:
		filtered = filtered[filtered["Gender"].astype(str).str.strip().str.title() == gender_value]
		filters["gender"] = gender

	contract_value = _normalize_text(contract)
	if contract_value:
		filtered = filtered[filtered["Contract Length"].astype(str).str.strip().str.lower() == contract_value]
		filters["contract"] = contract

	subscription_value = _normalize_text(subscription)
	if subscription_value:
		filtered = filtered[filtered["Subscription Type"].astype(str).str.strip().str.lower() == subscription_value]
		filters["subscription"] = subscription

	if churn is not None and "Churn" in filtered.columns:
		filtered = filtered[filtered["Churn"] == churn]
		filters["churn"] = churn

	total = len(filtered)
	total_pages = max((total + limit - 1) // limit, 1)
	page = min(page, total_pages)
	offset = (page - 1) * limit
	page_rows = filtered.iloc[offset:offset + limit]
	previous_link = str(request.url.include_query_params(page=page - 1, limit=limit)) if page > 1 else None
	next_link = str(request.url.include_query_params(page=page + 1, limit=limit)) if page < total_pages else None

	return UserSearchResponse(
		page=page,
		limit=limit,
		total=total,
		total_pages=total_pages,
		previous=previous_link,
		next=next_link,
		filters=filters,
		data=page_rows.to_dict(orient="records"),
	)
