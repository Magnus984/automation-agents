from fastapi import APIRouter
from api.utils.commute_calculator import calculate_commute_cost as compute_cost
from api.utils.address_to_coordinates import get_coordinates


location_component = APIRouter(tags=["Location Components"])


@location_component.get("/commute-cost")
def calculate_commute_cost(
    start_lat: float, start_lon: float,
    end_lat: float, end_lon: float,
    cost_per_km: float,
    workdays: int = 261,
):
    """
    Calculates the total commute cost for a given year based on distance and cost per km.
    Uses Google Maps API for route-based distance calculation.
    """
    return compute_cost(start_lat, start_lon, end_lat, end_lon, cost_per_km, workdays)


@location_component.get("/get-coordinates")
def fetch_coordinates(address: str):
    """
    Fetches latitude and longitude for a given address using Google Maps API.
    """
    return get_coordinates(address)