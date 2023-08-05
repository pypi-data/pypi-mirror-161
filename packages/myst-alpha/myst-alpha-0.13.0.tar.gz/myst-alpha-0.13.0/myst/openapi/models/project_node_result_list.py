from typing import List, Union

from myst.models import base_model
from myst.openapi.models.model_fit_result_list_item import ModelFitResultListItem
from myst.openapi.models.model_run_result_list_item import ModelRunResultListItem
from myst.openapi.models.operation_run_result_get import OperationRunResultGet
from myst.openapi.models.source_run_result_get import SourceRunResultGet
from myst.openapi.models.time_series_insert_result_get import TimeSeriesInsertResultGet
from myst.openapi.models.time_series_run_result_list_item import TimeSeriesRunResultListItem


class ProjectNodeResultList(base_model.BaseModel):
    """Project result list schema."""

    data: List[
        Union[
            SourceRunResultGet,
            ModelRunResultListItem,
            OperationRunResultGet,
            TimeSeriesRunResultListItem,
            TimeSeriesInsertResultGet,
            ModelFitResultListItem,
        ]
    ]
    has_more: bool
