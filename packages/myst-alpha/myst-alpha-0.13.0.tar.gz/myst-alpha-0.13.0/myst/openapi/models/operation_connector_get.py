from typing import Any, Dict, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class OperationConnectorGet(base_model.BaseModel):
    """Schema for operation connector get responses."""

    object_: Literal["Connector"] = Field(..., alias="object")
    type: Literal["OperationConnector"]
    uuid: str
    title: str
    provider: str
    description: str
    parameters_schema: Dict[str, Any]
    icon_url: Optional[str] = None
