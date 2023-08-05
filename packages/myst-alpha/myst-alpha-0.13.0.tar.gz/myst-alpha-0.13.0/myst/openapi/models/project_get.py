from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.deploy_status import DeployStatus
from myst.openapi.models.org_sharing_role import OrgSharingRole


class ProjectGet(base_model.BaseModel):
    """Schema for project get responses."""

    object_: Literal["Project"] = Field(..., alias="object")
    uuid: str
    create_time: str
    organization: str
    owner: str
    title: str
    creator: str
    deploy_status: DeployStatus
    organization_sharing_enabled: bool
    update_time: Optional[str] = None
    description: Optional[str] = None
    organization_sharing_role: Optional[OrgSharingRole] = None
