from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class OrganizationCreate(base_model.BaseModel):
    """Schema for organization create requests."""

    object_: Literal["Organization"] = Field(..., alias="object")
    name: str
