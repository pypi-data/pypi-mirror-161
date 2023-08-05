from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.models.types import UNSET, ItemOrSlice, OptionalArgument, Unset, UUIDOrStr
from myst.openapi.api.projects.models.inputs import (
    create_model_input,
    get_model_input,
    list_model_inputs,
    update_model_input,
)
from myst.openapi.api.projects.operations.inputs import (
    create_operation_input,
    get_operation_input,
    list_operation_inputs,
    update_operation_input,
)
from myst.openapi.models.input_create import InputCreate
from myst.openapi.models.input_update import InputUpdate
from myst.resources.edge import Edge

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.model import Model
    from myst.resources.operation import Operation
    from myst.resources.project import Project
    from myst.resources.time_series import TimeSeries


class ModelInput(Edge):
    """An edge from a time series into a model."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        model: Union["Model", UUIDOrStr],
        time_series: Union["TimeSeries", UUIDOrStr],
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> "ModelInput":
        """Creates a new model input edge between the given nodes.

        Args:
            project: the project this edge belongs to
            model: the model into which data flows out of this edge
            time_series: the time series from which data flows into this edge
            group_name: the name of the group of inputs on the underlying model or operation connector to which to pass
                the data from this input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to the downstream
                node
            label_indexer: the slice of the upstream data to pass to the downstream node

        Returns:
            the newly created model input
        """
        input_create = InputCreate(
            object="Edge",
            type="Input",
            upstream_node=str(get_resource_uuid(time_series)),
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

        input_ = create_model_input.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            json_body=input_create,
        )

        return ModelInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr], uuid: UUIDOrStr
    ) -> "ModelInput":
        """Gets a specific model input by its identifier."""
        input_ = get_model_input.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            model_uuid=str(get_resource_uuid(model)),
            uuid=str(uuid),
        )

        return ModelInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr], model: Union["Model", UUIDOrStr]) -> List["ModelInput"]:
        """Lists all model inputs for specified model node."""
        inputs = list_model_inputs.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), model_uuid=str(get_resource_uuid(model))
        )

        return [ModelInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project))) for input_ in inputs.data]

    def update(
        self,
        time_series: OptionalArgument[Union["TimeSeries", UUIDOrStr]] = UNSET,
        group_name: OptionalArgument[str] = UNSET,
        output_index: OptionalArgument[int] = UNSET,
        label_indexer: OptionalArgument[ItemOrSlice] = UNSET,
    ) -> "ModelInput":
        """Updates the model input."""
        input_update: Dict[str, Any] = dict(
            object="Edge",
            type="Input",
            upstream_node=time_series
            if time_series is None or isinstance(time_series, Unset)
            else str(get_resource_uuid(time_series)),
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

        input_ = update_model_input.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            model_uuid=str(self.downstream_node),
            uuid=str(self.uuid),
            json_body=InputUpdate.parse_obj(drop_unset_values(input_update)),
        )

        return ModelInput.parse_obj(dict(input_.dict(), project=self.project))


class OperationInput(Edge):
    """An edge from a time series into an operation."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        operation: Union["Operation", UUIDOrStr],
        time_series: Union["TimeSeries", UUIDOrStr],
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> "OperationInput":
        """Creates a new operation input edge between the given nodes.

        Args:
            project: the project this edge belongs to
            operation: the operation into which data flows out of this edge
            time_series: the time series from which data flows into this edge
            group_name: the name of the group of inputs on the underlying model or operation connector to which to pass
                the data from this input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to the downstream
                node
            label_indexer: the slice of the upstream data to pass to the downstream node

        Returns:
            the newly created operation input
        """
        input_create = InputCreate(
            object="Edge",
            type="Input",
            upstream_node=str(get_resource_uuid(time_series)),
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

        input_ = create_operation_input.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            operation_uuid=str(get_resource_uuid(operation)),
            json_body=input_create,
        )

        return OperationInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], operation: Union["Operation", UUIDOrStr], uuid: UUIDOrStr
    ) -> "OperationInput":
        """Gets a specific operation input by its identifier."""
        input_ = get_operation_input.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            operation_uuid=str(get_resource_uuid(operation)),
            uuid=str(uuid),
        )

        return OperationInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(
        cls, project: Union["Project", UUIDOrStr], operation: Union["Operation", UUIDOrStr]
    ) -> List["OperationInput"]:
        """Lists all operation inputs for specified operation node."""
        inputs = list_operation_inputs.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            operation_uuid=str(get_resource_uuid(operation)),
        )

        return [
            OperationInput.parse_obj(dict(input_.dict(), project=get_resource_uuid(project))) for input_ in inputs.data
        ]

    def update(
        self,
        time_series: OptionalArgument[Union["TimeSeries", UUIDOrStr]] = UNSET,
        group_name: OptionalArgument[str] = UNSET,
        output_index: OptionalArgument[int] = UNSET,
        label_indexer: OptionalArgument[ItemOrSlice] = UNSET,
    ) -> "OperationInput":
        """Updates the operation input."""
        input_update: Dict[str, Any] = dict(
            object="Edge",
            type="Input",
            upstream_node=time_series
            if time_series is None or isinstance(time_series, Unset)
            else str(get_resource_uuid(time_series)),
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

        input_ = update_operation_input.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            operation_uuid=str(self.downstream_node),
            uuid=str(self.uuid),
            json_body=InputUpdate.parse_obj(drop_unset_values(input_update)),
        )

        return OperationInput.parse_obj(dict(input_.dict(), project=self.project))
