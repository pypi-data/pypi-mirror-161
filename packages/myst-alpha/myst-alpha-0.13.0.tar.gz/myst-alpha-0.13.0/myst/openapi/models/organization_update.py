from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class OrganizationUpdate(base_model.BaseModel):
    """Schema for organization update requests."""

    object_: Optional[Literal["Organization"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    name: Optional[str] = None
