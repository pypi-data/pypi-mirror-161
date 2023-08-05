from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.hpo_job_state import HPOJobState


class HPOJobGet(base_model.BaseModel):
    """HPO job schema for get responses."""

    object_: Literal["HPOJob"] = Field(..., alias="object")
    uuid: str
    create_time: str
    hpo: str
    schedule_time: str
    num_trials_completed: int
    update_time: Optional[str] = None
    state: Optional[HPOJobState] = HPOJobState.PENDING
    result: Optional[str] = None
