from typing import Any, Dict, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class SourceConnectorGet(base_model.BaseModel):
    """Schema for source connector get responses."""

    object_: Literal["Connector"] = Field(..., alias="object")
    type: Literal["SourceConnector"]
    uuid: str
    title: str
    provider: str
    description: str
    parameters_schema: Dict[str, Any]
    icon_url: Optional[str] = None
