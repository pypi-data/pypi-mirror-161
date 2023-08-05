from functools import singledispatch
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values
from myst.client import get_client
from myst.connectors.model_connector import ModelConnector
from myst.connectors.operation_connector import OperationConnector
from myst.connectors.source_connector import SourceConnector
from myst.core.time.time_delta import TimeDelta
from myst.models.enums import DeployStatus, OrgSharingRole
from myst.models.types import UNSET, AxisLabels, CoordinateLabels, OptionalArgument, Shape, UUIDOrStr, to_uuid
from myst.openapi.api.projects import create_project, get_project, list_projects, update_project
from myst.openapi.api.projects.edges import list_project_edges
from myst.openapi.api.projects.nodes import list_project_nodes
from myst.openapi.models.input_get import InputGet
from myst.openapi.models.layer_get import LayerGet
from myst.openapi.models.model_get import ModelGet
from myst.openapi.models.operation_get import OperationGet
from myst.openapi.models.org_sharing_role import OrgSharingRole as OAIOrgSharingRole
from myst.openapi.models.project_create import ProjectCreate
from myst.openapi.models.project_update import ProjectUpdate
from myst.openapi.models.source_get import SourceGet
from myst.openapi.models.time_series_get import TimeSeriesGet
from myst.resources.deployment import Deployment
from myst.resources.edge import Edge
from myst.resources.input import ModelInput, OperationInput
from myst.resources.layer import TimeSeriesLayer
from myst.resources.model import Model
from myst.resources.node import Node
from myst.resources.operation import Operation
from myst.resources.resource import ShareableResource
from myst.resources.source import Source
from myst.resources.time_series import TimeSeries

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.recipes.time_series_recipe import TimeSeriesRecipe


@singledispatch
def _parse_node(node: Union[TimeSeriesGet, SourceGet, OperationGet, ModelGet]) -> Node:
    raise NotImplementedError()


@_parse_node.register
def _parse_time_series(node: TimeSeriesGet) -> TimeSeries:
    return TimeSeries.parse_obj(node.dict())


@_parse_node.register
def _parse_source(node: SourceGet) -> Source:
    return Source.parse_obj(node.dict())


@_parse_node.register
def _parse_model(node: ModelGet) -> Model:
    return Model.parse_obj(node.dict())


@_parse_node.register
def _parse_operation(node: OperationGet) -> Operation:
    return Operation.parse_obj(node.dict())


@singledispatch
def _parse_edge(edge: Union[InputGet, LayerGet], nodes: List[Node]) -> Edge:
    raise NotImplementedError()


@_parse_edge.register
def _parse_input(edge: InputGet, nodes: List[Node]) -> Union[ModelInput, OperationInput]:
    node = next((node for node in nodes if str(node.uuid) == edge.downstream_node), None)
    if node is None:
        raise ValueError("Could not find `downstream_node`.")
    if isinstance(node, Model):
        return ModelInput.parse_obj(dict(edge.dict(), project=node.project))
    else:
        return OperationInput.parse_obj(dict(edge.dict(), project=node.project))


@_parse_edge.register
def _parse_layer(edge: LayerGet, nodes: List[Node]) -> TimeSeriesLayer:
    node = next((node for node in nodes if str(node.uuid) == edge.downstream_node), None)
    if node is None:
        raise ValueError("Could not find `downstream_node`.")
    return TimeSeriesLayer.parse_obj(dict(edge.dict(), project=node.project))


class Project(ShareableResource):
    """A workspace for creating and deploying graphs of time series.

    A project collects the nodes and edges of the graph along with any policies used to execute the graph.
    """

    title: str
    deploy_status: DeployStatus
    description: Optional[str] = None

    @classmethod
    def create(
        cls,
        title: str,
        description: Optional[str] = None,
        organization_sharing_enabled: bool = False,
        organization_sharing_role: Optional[OrgSharingRole] = None,
    ) -> "Project":
        """Creates a new project.

        Args:
            title: the title of the project
            description: a brief description of the project
            organization_sharing_enabled: whether the project should be shared with the organization
            organization_sharing_role: the level of sharing access to this project to give users in the organization

        Returns:
            the newly created project
        """
        project = create_project.request_sync(
            client=get_client(),
            json_body=ProjectCreate(
                object="Project",
                title=title,
                description=description,
                organization_sharing_enabled=organization_sharing_enabled,
                organization_sharing_role=organization_sharing_role and OAIOrgSharingRole(organization_sharing_role),
            ),
        )

        return Project.parse_obj(project.dict())

    @classmethod
    def list(cls) -> List["Project"]:
        """Lists all projects visible to the user."""
        projects = list_projects.request_sync(client=get_client())

        return [Project.parse_obj(project.dict()) for project in projects.data]

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "Project":
        """Gets a specific project by its identifier."""
        project = get_project.request_sync(client=get_client(), uuid=str(to_uuid(uuid)))

        return Project.parse_obj(project.dict())

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        description: OptionalArgument[str] = UNSET,
        organization_sharing_enabled: OptionalArgument[bool] = UNSET,
        organization_sharing_role: OptionalArgument[OrgSharingRole] = UNSET,
    ) -> "Project":
        """Updates the project."""
        project_update: Dict[str, Any] = dict(
            object="Project",
            title=title,
            description=description,
            organization_sharing_enabled=organization_sharing_enabled,
            organization_sharing_role=organization_sharing_role and OAIOrgSharingRole(organization_sharing_role)
            if isinstance(organization_sharing_role, OrgSharingRole)
            else organization_sharing_role,
        )

        project = update_project.request_sync(
            client=get_client(),
            uuid=str(self.uuid),
            json_body=ProjectUpdate.parse_obj(drop_unset_values(project_update)),
        )

        return Project.parse_obj(project)

    def list_nodes(self) -> List[Node]:
        """Lists all nodes in this project."""
        project_nodes = list_project_nodes.request_sync(client=get_client(), project_uuid=str(self.uuid))

        return [_parse_node(node) for node in project_nodes.data]

    def list_edges(self) -> List[Edge]:
        """Lists all edges in this project."""
        project_edges = list_project_edges.request_sync(client=get_client(), project_uuid=str(self.uuid))

        return [_parse_edge(edge, nodes=self.list_nodes()) for edge in project_edges.data]

    def create_source(self, title: str, connector: SourceConnector, description: Optional[str] = None) -> Source:
        """Creates a new source node in this project.

        Args:
            title: the title of the source
            connector: specification of the connector this source should use
            description: a brief description of the source

        Returns:
            the newly created source
        """
        return Source.create(project=self, title=title, connector=connector, description=description)

    def create_model(self, title: str, connector: ModelConnector, description: Optional[str] = None) -> Model:
        """Creates a new model node in this project.

        Args:
            title: the title of the model
            connector: specification of the connector this model should use
            description: a brief description of the model

        Returns:
            the newly created model
        """
        return Model.create(project=self, title=title, connector=connector, description=description)

    def create_operation(
        self, title: str, connector: OperationConnector, description: Optional[str] = None
    ) -> Operation:
        """Creates a new operation node in this project.

        Args:
            title: the title of the operation
            connector: specification of the connector this operation should use
            description: a brief description of the operation

        Returns:
            the newly created operation
        """
        return Operation.create(project=self, title=title, connector=connector, description=description)

    def create_time_series(
        self,
        title: str,
        sample_period: TimeDelta,
        cell_shape: Shape = (),
        coordinate_labels: CoordinateLabels = (),
        axis_labels: AxisLabels = (),
        description: Optional[str] = None,
    ) -> TimeSeries:
        """Creates a new time series node in this project.

        Args:
            title: the title of the time series
            sample_period: the frequency at which the data is sampled
            cell_shape: the shape of the data in each cell of the time series
            coordinate_labels: the labels for each coordinate of a cell in the time series
            axis_labels: the labels for each axis of a cell in the time series
            description: a brief description of the time series

        Returns:
            the newly created time series
        """
        return TimeSeries.create(
            project=self,
            title=title,
            sample_period=sample_period,
            cell_shape=cell_shape,
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
            description=description,
        )

    def create_time_series_from_recipe(
        self, recipe: "TimeSeriesRecipe", title: Optional[str] = None, description: Optional[str] = None
    ) -> TimeSeries:
        """Creates a new time series node in this project based on a provided recipe.

        Args:
            recipe: the recipe used to create the time series
            title: the title of the time series; if none is given, the recipe will supply a sensible default
            description: the description of the time series

        Returns:
            the newly created time series
        """
        return recipe.create(project=self, title=title, description=description)

    def deploy(self, title: str) -> Deployment:
        """Deploys the current project.

        Args:
            title: the title for the deployment

        Returns:
            the newly created deployment
        """
        return Deployment.create(project=self, title=title)
