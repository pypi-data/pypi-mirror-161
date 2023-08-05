from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.deploy_status import DeployStatus
from myst.openapi.models.org_sharing_role import OrgSharingRole


class ProjectUpdate(base_model.BaseModel):
    """Schema for project update requests."""

    object_: Optional[Literal["Project"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    organization: Optional[str] = None
    owner: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    organization_sharing_enabled: Optional[bool] = None
    organization_sharing_role: Optional[OrgSharingRole] = None
    creator: Optional[str] = None
    deploy_status: Optional[DeployStatus] = None
