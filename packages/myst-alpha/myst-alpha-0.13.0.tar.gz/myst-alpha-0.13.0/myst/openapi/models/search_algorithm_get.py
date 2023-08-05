from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class SearchAlgorithmGet(base_model.BaseModel):
    """Search algorithm schema for get responses."""

    type: Literal["Hyperopt"]
    metric: Literal["mse"]
    num_trials: int
    max_concurrent_trials: int
    object_: Optional[Literal["SearchAlgorithm"]] = Field(..., alias="object")
