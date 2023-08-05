from typing import Dict, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.models.time_dataset import TimeDataset


class ModelRunResultGet(base_model.BaseModel):
    """Schema for model run result get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["ModelRunResult"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    inputs: Dict[str, Optional[List[TimeDataset]]]
    outputs: List[TimeDataset]
    update_time: Optional[str] = None
