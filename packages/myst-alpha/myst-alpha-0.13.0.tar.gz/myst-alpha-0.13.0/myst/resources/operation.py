from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.connectors.operation_connector import OperationConnector
from myst.models.types import UNSET, ItemOrSlice, OptionalArgument, UUIDOrStr, to_uuid
from myst.openapi.api.projects.operations import create_operation, get_operation, update_operation
from myst.openapi.models.operation_create import OperationCreate
from myst.openapi.models.operation_update import OperationUpdate
from myst.resources.connector_node import ConnectorNode
from myst.resources.input import OperationInput
from myst.resources.time_series import TimeSeries

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Operation(ConnectorNode):
    """A node that performs a specified transformation on its input.

    In contrast to a model, an operation has no training phase and can only be run.
    """

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        title: str,
        connector: OperationConnector,
        description: Optional[str] = None,
    ) -> "Operation":
        """Creates a new operation node.

        Args:
            project: the project in which to create the operation
            title: the title of the operation
            connector: the operation connector to use in the operation node
            description: a brief description of the operation

        Returns:
            the newly created operation
        """
        operation = create_operation.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            json_body=OperationCreate(
                object="Node",
                type="Operation",
                title=title,
                description=description,
                connector_uuid=str(connector.uuid),
                parameters=connector.parameters_exclude_none(),
            ),
        )

        return Operation.parse_obj(operation.dict())

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "Operation":
        """Gets a specific operation by its identifier."""
        operation = get_operation.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), uuid=str(to_uuid(uuid))
        )

        return Operation.parse_obj(operation.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["Operation"]:
        """Gets all operations by project."""
        raise NotImplementedError()

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        connector: OptionalArgument[OperationConnector] = UNSET,
        description: OptionalArgument[str] = UNSET,
    ) -> "Operation":
        """Updates operation."""
        parameters = connector.parameters_exclude_none() if isinstance(connector, OperationConnector) else UNSET
        operation_update: Dict[str, Any] = dict(
            object="Node",
            type="Operation",
            title=title,
            connector_uuid=str(connector.uuid) if isinstance(connector, OperationConnector) else UNSET,
            parameters=parameters,
            description=description,
        )

        operation = update_operation.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=OperationUpdate.parse_obj(drop_unset_values(operation_update)),
        )

        return Operation.parse_obj(operation.dict())

    def create_input(
        self,
        time_series: Union[TimeSeries, UUIDOrStr],
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> OperationInput:
        """Creates an input into this operation.

        Args:
            time_series: the time series to feed into this operation
            group_name: the name of the input group on this operation's connector to which to pass the data from this
                input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this operation
            label_indexer: the slice of the upstream data to pass to this operation

        Returns:
            the newly created input
        """
        return OperationInput.create(
            project=self.project,
            operation=self.uuid,
            time_series=time_series,
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

    def list_inputs(self) -> List[OperationInput]:
        """Lists all inputs into this operation."""
        return OperationInput.list(project=self.project, operation=self.uuid)
