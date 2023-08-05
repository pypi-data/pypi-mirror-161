from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.organization_role import OrganizationRole


class UserGet(base_model.BaseModel):
    """Schema for user get responses."""

    object_: Literal["User"] = Field(..., alias="object")
    uuid: str
    create_time: str
    email: str
    organization: str
    organization_role: OrganizationRole
    update_time: Optional[str] = None
