from typing import Any, Dict, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.deploy_status import DeployStatus
from myst.openapi.models.time_dataset_spec import TimeDatasetSpec


class OperationUpdate(base_model.BaseModel):
    """Schema for operation update requests."""

    object_: Optional[Literal["Node"]] = Field(..., alias="object")
    uuid: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    organization: Optional[str] = None
    owner: Optional[str] = None
    type: Optional[Literal["Operation"]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    project: Optional[str] = None
    deploy_status: Optional[DeployStatus] = None
    connector_uuid: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    output_specs: Optional[List[TimeDatasetSpec]] = None
    input_specs_schema: Optional[Dict[str, Any]] = None
