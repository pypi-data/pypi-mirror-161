from typing import Dict, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class BacktestResultGet(base_model.BaseModel):
    """Schema for model fit result get responses."""

    object_: Literal["BacktestResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    start_time: str
    end_time: str
    result_url: str
    metrics: Optional[Dict[str, Optional[float]]] = None
