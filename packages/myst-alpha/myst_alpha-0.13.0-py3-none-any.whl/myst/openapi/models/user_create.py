from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.organization_role import OrganizationRole


class UserCreate(base_model.BaseModel):
    """Schema for user create requests."""

    object_: Literal["User"] = Field(..., alias="object")
    email: str
    organization: str
    organization_role: OrganizationRole
