from typing import Any, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.deploy_status import DeployStatus


class TimeSeriesUpdate(base_model.BaseModel):
    """Schema for time series update requests."""

    object_: Optional[Literal["Node"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    organization: Optional[str] = None
    owner: Optional[str] = None
    type: Optional[Literal["TimeSeries"]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    project: Optional[str] = None
    deploy_status: Optional[DeployStatus] = None
    sample_period: Optional[str] = None
    cell_shape: Optional[List[Any]] = None
    coordinate_labels: Optional[List[Any]] = None
    axis_labels: Optional[List[Any]] = None
