import requests
from api.core.config import settings

def get_coordinates(address):
    """
    Converts an address to latitude and longitude using Google Maps API.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = settings.google_api_key
    params = {
        "address": address,
        "key": f"{api_key}"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] != "OK":
        return {"error": "Failed to retrieve coordinates", "details": data}
    
    location = data["results"][0]["geometry"]["location"]
    return {
        "latitude": location["lat"],
        "longitude": location["lng"]
    }



start_address = "Bahnhofstrasse 1, 8001 Zürich, Switzerland"
print(get_coordinates(start_address))


end_address = "Pilatusstrasse 1, 6003 Luzern, Switzerland"
print(get_coordinates(end_address))