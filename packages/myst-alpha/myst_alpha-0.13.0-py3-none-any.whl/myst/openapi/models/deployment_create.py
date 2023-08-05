from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class DeploymentCreate(base_model.BaseModel):
    """Schema for deployment create requests."""

    title: str
    object_: Optional[Literal["Deployment"]] = Field("Deployment", alias="object")
