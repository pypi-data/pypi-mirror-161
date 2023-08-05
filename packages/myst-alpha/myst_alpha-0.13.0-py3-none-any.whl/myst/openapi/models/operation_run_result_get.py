from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class OperationRunResultGet(base_model.BaseModel):
    """Schema for operation run result get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["OperationRunResult"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    update_time: Optional[str] = None
