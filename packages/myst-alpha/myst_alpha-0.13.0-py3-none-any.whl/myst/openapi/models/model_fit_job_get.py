from typing import List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.job_error import JobError
from myst.openapi.models.job_state import JobState


class ModelFitJobGet(base_model.BaseModel):
    """Model fit job schema for get responses."""

    object_: Literal["NodeJob"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["ModelFitJob"]
    node: str
    errors: List[JobError]
    start_time: str
    end_time: str
    as_of_time: str
    state: JobState
    update_time: Optional[str] = None
    result: Optional[str] = None
    error_reason: Optional[str] = None
    error_edge: Optional[str] = None
