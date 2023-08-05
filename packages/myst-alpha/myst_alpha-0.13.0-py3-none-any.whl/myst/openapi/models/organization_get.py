from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class OrganizationGet(base_model.BaseModel):
    """Schema for organization get responses."""

    object_: Literal["Organization"] = Field(..., alias="object")
    uuid: str
    create_time: str
    name: str
    update_time: Optional[str] = None
