import requests
from api.core.config import settings

def calculate_commute_cost(start_lat, start_lon, end_lat, end_lon, cost_per_km, workdays):
    """
    Uses Google Maps API to calculate the route-based commute cost.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    api_key = settings.google_api_key
    params = {
        "origin": f"{start_lat},{start_lon}",
        "destination": f"{end_lat},{end_lon}",
        "key": f"{api_key}",
        "mode": "driving"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] != "OK":
        return {"error": "Failed to retrieve distance from Google Maps API", "details": data}
    
    distance_meters = data["routes"][0]["legs"][0]["distance"]["value"]
    distance_km = distance_meters / 1000  # Convert meters to km
    
    daily_cost = distance_km * 2 * cost_per_km  # Round trip cost per day
    total_cost = daily_cost * workdays
    
    return {
        "trips": workdays,
        "one_way_distance_km": distance_km,
        "round_trip_cost": daily_cost,
        "total_commute_cost": total_cost
    }
    
    