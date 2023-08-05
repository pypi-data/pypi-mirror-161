from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.organization_role import OrganizationRole


class UserUpdate(base_model.BaseModel):
    """Schema for user update requests."""

    object_: Optional[Literal["User"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    email: Optional[str] = None
    organization: Optional[str] = None
    organization_role: Optional[OrganizationRole] = None
