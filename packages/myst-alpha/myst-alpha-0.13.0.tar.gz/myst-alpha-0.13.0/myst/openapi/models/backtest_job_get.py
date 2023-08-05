from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.job_state import JobState


class BacktestJobGet(base_model.BaseModel):
    """Abstract base job schema for get responses."""

    object_: Literal["BacktestJob"] = Field(..., alias="object")
    uuid: str
    backtest: str
    state: JobState
