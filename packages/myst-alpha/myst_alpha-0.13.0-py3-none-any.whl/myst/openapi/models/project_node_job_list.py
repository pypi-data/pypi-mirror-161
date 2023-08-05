from typing import List, Union

from myst.models import base_model
from myst.openapi.models.model_fit_job_get import ModelFitJobGet
from myst.openapi.models.node_run_job_get import NodeRunJobGet


class ProjectNodeJobList(base_model.BaseModel):
    """Project job list schema."""

    data: List[Union[NodeRunJobGet, ModelFitJobGet]]
    has_more: bool
