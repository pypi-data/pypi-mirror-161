from typing import List, Union

from myst.models import base_model
from myst.openapi.models.model_connector_get import ModelConnectorGet
from myst.openapi.models.operation_connector_get import OperationConnectorGet
from myst.openapi.models.source_connector_get import SourceConnectorGet


class PolymorphicConnectorList(base_model.BaseModel):
    """Schema for polymorphic connector list responses."""

    data: List[Union[SourceConnectorGet, OperationConnectorGet, ModelConnectorGet]]
    has_more: bool
