from fastapi import APIRouter, Query
import requests

lead_identifier = APIRouter(tags=["Lead Identifier"])

SERPAPI_KEY = "1b98b08bfe39cbdd9462dffb17fb0d8ce7156e319d77d82837f7c9bf97842cb9"

@lead_identifier.get("/lead_identifier")
def find_companies(
    location: str = Query(..., description="Company location"),
    industry: str = Query(..., description="Company industry"),
    company_size: str = Query(..., description="Company size, e.g., '11-50', '51-200'"),
    technology: str = Query(..., description="Technology used, e.g., 'AWS', 'Python'")
):
    """
    Searches for companies on LinkedIn based on location, industry, company size, and technology usage.
    """
    search_query = f"{industry} companies in {location} with {company_size} employees using {technology}"
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": search_query,
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("organic_results", [])
