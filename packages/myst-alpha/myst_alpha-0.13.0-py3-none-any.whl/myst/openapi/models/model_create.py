from typing import Any, Dict, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class ModelCreate(base_model.BaseModel):
    """Schema for model create requests."""

    title: str
    connector_uuid: str
    object_: Optional[Literal["Node"]] = Field("Node", alias="object")
    type: Optional[Literal["Model"]] = "Model"
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
