from typing import Any, Dict
import requests
from requests.exceptions import RequestException
from api.core.config import settings
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi import APIRouter
from api.v1.schemas.response_model import SuccessResponse, ErrorResponse

api_key_header = APIKeyHeader(name="Api-Key")

def auth_guard(
    client: str = "Web",
    auth: str = Security(api_key_header)
    ) -> Dict[str, Any]:
    """
    Validates the API key by calling the accounts service.
    
    Args:
        auth: The API key from the request header
        
    Returns:
        Dict containing user/account information
        
    Raises:
        HTTPException: If the API key is invalid or if there's an issue with the accounts service
    """
    try:
        response = requests.get(
            f"{settings.ACCOUNTS_SERVICE_URL.strip('/')}/api/v1/api_keys/validate_api_key",
            headers={"Api-Key": auth.strip()},
            timeout=5  # Add a reasonable timeout
        )
        print("response sent to validation api")
        if response.status_code == 401 or response.status_code == 403:
            raise HTTPException(401, "Invalid API Key")
        elif response.status_code != 200:
            raise HTTPException(500, "Authentication service error")
            
        response_data = response.json()
        # Ensure the response includes access_token or use the original API key
        if 'access_token' not in response_data:
            response_data['access_token'] = auth  # Use the original API key as the access token
        
        # add client to response data
        response_data['client'] = client

        return response_data
    except RequestException as e:
        # Handle network errors, timeouts, etc.
        raise HTTPException(503, f"Authentication service unavailable: {str(e)}")

