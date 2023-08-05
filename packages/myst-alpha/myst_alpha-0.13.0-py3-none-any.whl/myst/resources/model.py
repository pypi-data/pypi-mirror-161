from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.connectors.model_connector import ModelConnector
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.timing import ScheduleTiming, TimeRangeBoundary
from myst.models.types import UNSET, ItemOrSlice, OptionalArgument, UUIDOrStr, to_uuid
from myst.openapi.api.projects.models import create_model, get_model, update_model
from myst.openapi.models.model_create import ModelCreate
from myst.openapi.models.model_update import ModelUpdate
from myst.resources.connector_node import ConnectorNode
from myst.resources.input import ModelInput
from myst.resources.policy import ModelFitPolicy
from myst.resources.result import ModelFitResult, ModelRunResult, ModelRunResultMetadata
from myst.resources.time_series import TimeSeries

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Model(ConnectorNode):
    """A node that learns its parameters during a training phase, and produces output during a prediction phase."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        title: str,
        connector: ModelConnector,
        description: Optional[str] = None,
    ) -> "Model":
        """Creates a new model node.

        Args:
            project: the project in which to create the model
            title: the title of the model
            connector: the model connector to use in the model node
            description: a brief description of the model

        Returns:
            the newly created model
        """
        model = create_model.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            json_body=ModelCreate(
                object="Node",
                type="Model",
                title=title,
                description=description,
                connector_uuid=str(connector.uuid),
                parameters=connector.parameters_exclude_none(),
            ),
        )

        return Model.parse_obj(model.dict())

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "Model":
        """Gets a specific model by its identifier."""
        model = get_model.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), uuid=str(to_uuid(uuid))
        )

        return Model.parse_obj(model.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["Model"]:
        """Gets all models by project."""
        raise NotImplementedError()

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        connector: OptionalArgument[ModelConnector] = UNSET,
        description: OptionalArgument[str] = UNSET,
    ) -> "Model":
        """Updates model."""
        parameters = connector.parameters_exclude_none() if isinstance(connector, ModelConnector) else UNSET

        model_update: Dict[str, Any] = dict(
            object="Node",
            type="Model",
            title=title,
            connector_uuid=str(connector.uuid) if isinstance(connector, ModelConnector) else UNSET,
            parameters=parameters,
            description=description,
        )

        model = update_model.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=ModelUpdate.parse_obj(drop_unset_values(model_update)),
        )

        return Model.parse_obj(model.dict())

    def create_input(
        self,
        time_series: Union[TimeSeries, UUIDOrStr],
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> ModelInput:
        """Creates a model input into this model.

        Args:
            time_series: the time series to feed into this model
            group_name: the name of the input group on this model's connector to which to pass the data from this input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this model
            label_indexer: the slice of the upstream data to pass to this model

        Returns:
            the newly created input
        """
        return ModelInput.create(
            project=self.project,
            model=self.uuid,
            time_series=time_series,
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

    def list_inputs(self) -> List[ModelInput]:
        """Lists all model inputs into this model."""
        return ModelInput.list(project=str(self.project), model=self.uuid)

    def create_fit_policy(
        self,
        schedule_timing: Union[Time, TimeDelta, ScheduleTiming],
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        active: bool = True,
    ) -> ModelFitPolicy:
        return ModelFitPolicy.create(
            project=self.project,
            model=self.uuid,
            schedule_timing=schedule_timing,
            start_timing=start_timing,
            end_timing=end_timing,
            active=active,
        )

    def list_fit_policies(self) -> List[ModelFitPolicy]:
        return ModelFitPolicy.list(project=self.project, model=self.uuid)

    def list_fit_results(self) -> List[ModelFitResult]:
        return ModelFitResult.list(project=self.project, model=self.uuid)

    def get_fit_result(self, uuid: UUIDOrStr) -> ModelFitResult:
        return ModelFitResult.get(project=self.project, model=self.uuid, uuid=uuid)

    def list_run_results(self) -> List[ModelRunResultMetadata]:
        return ModelRunResult.list(project=self.project, model=self.uuid)

    def get_run_result(self, model_result: Union[ModelRunResultMetadata, UUIDOrStr]) -> ModelRunResult:
        return ModelRunResult.get(project=self.project, model=self.uuid, uuid=get_resource_uuid(model_result))
