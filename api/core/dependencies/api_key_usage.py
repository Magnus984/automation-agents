from typing import Dict, Union
from datetime import datetime
from api.v1.schemas.response_model import (
                        SuccessResponse,
                        ErrorResponse,
                        ErrorData)
import requests
from api.core.config import settings
import json

def send_report(
    auth: Dict[str, Union[str, bool]],
    client: str,
    endpoint: str,
):
    """
    Send a report to the reporting service.
    
    Args:
        auth: The API key from the request header
        
    Returns:
        Dict containing the status of the report submission
    """
    payload = {
        "client": client,
        "model_identifier": endpoint,
    }
    print("Payload: ", payload)
    print("token: ", auth["access_token"])
    try:
        response = requests.post(
            f"{settings.ACCOUNTS_SERVICE_URL}/api/v1/api_keys/report_usage",
            headers={
                "Api-Key": auth['access_token'],
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            data=json.dumps(payload),
            timeout=10  # Add timeout to prevent hanging
        )
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        success_response = SuccessResponse(
            status_code=response.status_code,
            message="Report sent successfully",
            data=response.json()
        )
        
        return success_response
    
    except requests.exceptions.RequestException as e:
        error_data = ErrorData(
                error=str(e),
                error_type=type(e).__name__
            )
        error_response = ErrorResponse(
            status_code=response.status_code,
            message="Failed to send report",
            data=ErrorData(
                error=str(e),
                error_type=type(e).__name__
            )
        )

        return error_response