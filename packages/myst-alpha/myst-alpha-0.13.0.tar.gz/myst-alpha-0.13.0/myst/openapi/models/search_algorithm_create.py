from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class SearchAlgorithmCreate(base_model.BaseModel):
    """Search algorithm schema for create responses."""

    object_: Optional[Literal["SearchAlgorithm"]] = Field(..., alias="object")
    type: Optional[Literal["Hyperopt"]] = "Hyperopt"
    metric: Optional[Literal["mse"]] = "mse"
    num_trials: Optional[int] = 10
    max_concurrent_trials: Optional[int] = 1
