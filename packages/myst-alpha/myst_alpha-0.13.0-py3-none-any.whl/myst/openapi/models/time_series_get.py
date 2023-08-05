from typing import Any, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.deploy_status import DeployStatus


class TimeSeriesGet(base_model.BaseModel):
    """Schema for time series get responses."""

    object_: Literal["Node"] = Field(..., alias="object")
    uuid: str
    create_time: str
    organization: str
    owner: str
    type: Literal["TimeSeries"]
    title: str
    project: str
    creator: str
    deploy_status: DeployStatus
    sample_period: str
    cell_shape: List[Any]
    coordinate_labels: List[Any]
    axis_labels: List[Any]
    update_time: Optional[str] = None
    description: Optional[str] = None
