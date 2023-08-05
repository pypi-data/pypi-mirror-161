from typing import List, Union

from myst.models import base_model
from myst.openapi.models.model_fit_policy_get import ModelFitPolicyGet
from myst.openapi.models.time_series_run_policy_get import TimeSeriesRunPolicyGet


class ProjectNodePolicyList(base_model.BaseModel):
    """Schema for a list of project policies."""

    data: List[Union[TimeSeriesRunPolicyGet, ModelFitPolicyGet]]
    has_more: bool
