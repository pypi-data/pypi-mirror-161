from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.org_sharing_role import OrgSharingRole


class ProjectCreate(base_model.BaseModel):
    """Schema for project create requests."""

    title: str
    object_: Optional[Literal["Project"]] = Field("Project", alias="object")
    description: Optional[str] = None
    organization_sharing_enabled: Optional[bool] = False
    organization_sharing_role: Optional[OrgSharingRole] = None
