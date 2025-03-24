from fastapi import APIRouter, Depends, HTTPException
from api.utils.commute_calculator import calculate_commute_cost as compute_cost
from api.utils.address_to_coordinates import get_coordinates
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Dict, Union


location_component = APIRouter(tags=["Location Components"])


@location_component.get("/commute-cost")
def calculate_commute_cost(
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float,
    cost_per_km: float,
    workdays: int = 261,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
):
    """
    Calculates the total commute cost for a given year based on distance and cost per km.
    Uses Google Maps API for route-based distance calculation.
    """

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "GET /commute-cost",
        )

        print(report)
    
    return compute_cost(start_lat, start_lon, end_lat, end_lon, cost_per_km, workdays)


@location_component.get("/get-coordinates")
def fetch_coordinates(
    address: str,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    """
    Fetches latitude and longitude for a given address using Google Maps API.
    """

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "GET /get-coordinates",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )

    return get_coordinates(address)