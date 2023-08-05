from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class DeploymentGet(base_model.BaseModel):
    """Schema for deployment get responses."""

    object_: Literal["Deployment"] = Field(..., alias="object")
    uuid: str
    create_time: str
    title: str
    creator: str
    update_time: Optional[str] = None
    activate_time: Optional[str] = None
    deactivate_time: Optional[str] = None
