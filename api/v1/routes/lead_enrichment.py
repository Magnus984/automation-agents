from fastapi import APIRouter, Query, Depends, HTTPException
import requests
from api.core.config import settings
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Dict, Union

lead_enrichment = APIRouter(tags=["Lead Enrichment"])


@lead_enrichment.get("/lead_enrichment")
def find_leads(
    company_name: str = Query(..., description="Company name. eg. 4th-ir"),
    company_domain: str = Query(..., description="Company domain. e.g: https://4th-ir.com/"),
    target_role: str = Query(..., description="Target role"),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
):
    try: 
        """
        Searches for people from companies.
        """
        
        url = "https://api.skrapp.io/profile/search/email"

        params = {
            "companyName": company_name,
            "size": 10,
            "companyWebsite":company_domain,
            # "title": f"{target_role}",
            "title": target_role
        }

        lead_enrichment_key = settings.LEAD_ENRICHMENT_KEY

        headers = {
            "X-Access-Key": lead_enrichment_key,
            "Content-Type": "application/json"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        filtered_results = [
        {
            "first_name": person["first_name"],
            "last_name": person["last_name"],
            "full_name": person["full_name"],
            "location": person["location"],
            "title": person["position"]["title"],
            "email": person["email"]
        }
        for person in data["results"]
        if person["email_quality"]["status"] == "valid"
        ]

        if auth["is_valid"]:
            report = send_report(
                auth,
                auth['client'],
                "GET /lead_enrichment",
            )

            if report.status == "error":
                raise HTTPException(
                    status_code=report.status_code,
                    detail=report.data.error
                )
        return filtered_results
    
    except Exception as e:
        return []
