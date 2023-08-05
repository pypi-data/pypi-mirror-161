from typing import List, Optional

from myst.models.base_model import BaseModel


class ValidationError(BaseModel):
    """Model for validation error details returned by the server."""

    loc: List[str]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """Model for a validation error (HTTP 422) returned by the API."""

    detail: Optional[List[ValidationError]] = None


class StringDetailError(BaseModel):
    """Pydantic model used to describe a simple string detail error."""

    detail: str
