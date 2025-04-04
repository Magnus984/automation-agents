from fastapi import (
                    HTTPException,
                    Body, Depends, Request, 
                    APIRouter, status)
from fastapi.responses import JSONResponse, StreamingResponse
from api.v1.schemas.base64_schemas import EncodeText, DecodeText
from api.v1.schemas.response_model import (
                                SuccessResponse,
                                ErrorData, ErrorResponse)
from api.utils.keywordextractor import extract_keywords
from api.core.dependencies.llm import analyze_emails
from pydantic import BaseModel
from typing import List, Dict, Union
import base64
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report

email_reading = APIRouter(tags=["Email Reading Tools"])

@email_reading.post("/extract_keywords")
async def api_extract_keywords(
    text,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    try:
        keywords = extract_keywords(text)

        if auth["is_valid"]:
                report = send_report(
                    auth,
                    auth['client'],
                    "GET /analyze_emails",
                )

                if report.status == "error":
                    raise HTTPException(
                        status_code=report.status_code,
                        detail=report.data.error
                    )

        return JSONResponse({"keywords": keywords})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during keyword extraction: {e}"
        )


class EmailRequest(BaseModel):
    emails: List[Dict[str, str]]  # List of email dictionaries


@email_reading.post("/analyze_emails")
async def api_analyze_emails(
    question,
    request: EmailRequest, 
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    try:
        response = analyze_emails(request.emails, question)
        if response:
            if auth["is_valid"]:
                report = send_report(
                    auth,
                    auth['client'],
                    "GET /analyze_emails",
                )

                if report.status == "error":
                    raise HTTPException(
                        status_code=report.status_code,
                        detail=report.data.error
                    )

            return JSONResponse({"response": response})
        else:
            raise HTTPException(
                status_code=500,
                detail="ChatGPT response was empty or an error occurred.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during ChatGPT interaction: {e}"
        )

@email_reading.post("/encode",
            tags=["Email Reading Tools"],
            response_model=SuccessResponse,
            responses={
                        200: {
                            "model": SuccessResponse,
                            "description": "Encoding successfull"
                          },
                        500: {
                            "model": ErrorResponse,
                            "description": "Failed to encode text"
                          }
            })
def text_to_base64(
    request: EncodeText,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    """Converts text to base64 encoding"""
    try:
        # converts text to bytes
        bytes_data = request.text.encode()
        # perform encoding on bytes-like object
        encoded_data = base64.b64encode(bytes_data)
        
        success_response = SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Encoding successfull",
            data={
                "encoded_data": f"{encoded_data.decode()}"
            }
        )

        if auth["is_valid"]:
            report = send_report(
                auth,
                auth['client'],
                "GET /encode",
            )

            if report.status == "error":
                raise HTTPException(
                    status_code=report.status_code,
                    detail=report.data.error
                )
        
        return success_response
    except Exception as e:
        error_response = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to encode text",
            data=ErrorData(
                error=str(e), error_type=type(e).__name__
            )
        )
        return error_response

@email_reading.post("/decode",
            tags=["Email Reading Tools"],
            response_model=SuccessResponse,
            responses={
                        200: {
                            "model": SuccessResponse,
                            "description": "Decoding successfull"
                          },
                        500: {
                            "model": ErrorResponse,
                            "description": "Failed to decode text"
                          }
            })
def base64_to_text(
    request: DecodeText,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    """Converts base64 encoding to text"""
    try:
        # convert encoding to bytes
        bytes_data = request.base64_string.encode()

        # perform decoding on encoded bytes-like string
        decoded_data = base64.b64decode(bytes_data)

        success_response = SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Encoding successfull",
            data={
                "decoded_data": f"{decoded_data.decode()}"
            }
        )

        if auth["is_valid"]:
            report = send_report(
                auth,
                auth['client'],
                "POST /decode",
            )

            if report.status == "error":
                raise HTTPException(
                    status_code=report.status_code,
                    detail=report.data.error
                )
        
        return success_response
    except Exception as e:
        error_response = ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to decode text",
            data=ErrorData(
                str(e), type(e).__name
            )
        )
        return error_response
