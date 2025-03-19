"""Response model module"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    """Standard API response model for both success and error responses."""
    status: str = Field(
        ..., description="Status of the response (success or error)")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data payload")


class SuccessResponse(StandardResponse):
    status: str = "success"


class ErrorData(BaseModel):
    """Container for error data."""
    error: Optional[str] = None
    error_type: Optional[str] = None


class ErrorResponse(StandardResponse):
    """Response model for generic errors."""
    status: str = "error"
    data: ErrorData = Field(..., description="Error details")