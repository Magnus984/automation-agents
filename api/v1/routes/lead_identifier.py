from fastapi import APIRouter, Query, Depends, HTTPException
import requests
from api.core.config import settings
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Dict, Union

lead_identifier = APIRouter(tags=["Lead Identifier"], dependencies=[Depends(auth_guard)])


@lead_identifier.get("/lead_identifier")
def find_companies(
    location: str = Query(..., description="Company location"),
    industry: str = Query(..., description="Company industry"),
    company_size: str = Query(..., description="Company size, e.g., '11-50', '51-200'"),
    technology: str = Query(..., description="Technology used, e.g., 'AWS', 'Python'"),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
):
    """
    Searches for companies on LinkedIn based on location, industry, company size, and technology usage.
    """
    search_query = f"{industry} companies in {location} with {company_size} employees using {technology}"
    api_key = settings.SERPAPI_KEY
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": search_query,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "GET /lead_identifier",
        )
        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
    return data.get("organic_results", [])
