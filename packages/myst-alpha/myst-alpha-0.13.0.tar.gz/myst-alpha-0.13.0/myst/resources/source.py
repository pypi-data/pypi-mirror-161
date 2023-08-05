from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.connectors.source_connector import SourceConnector
from myst.models.types import UNSET, OptionalArgument, UUIDOrStr, to_uuid
from myst.openapi.api.projects.sources import create_source, get_source, update_source
from myst.openapi.models.source_create import SourceCreate
from myst.openapi.models.source_update import SourceUpdate
from myst.resources.connector_node import ConnectorNode

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Source(ConnectorNode):
    """A node which produces data without any inputs."""

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        title: str,
        connector: SourceConnector,
        description: Optional[str] = None,
    ) -> "Source":
        """Creates a new source node.

        Args:
            project: the project in which to create the source
            title: the title of the source
            connector: the source connector to use in the source node
            description: a brief description of the source

        Returns:
            the newly created source
        """
        source = create_source.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            json_body=SourceCreate(
                object="Node",
                type="Source",
                title=title,
                description=description,
                connector_uuid=str(connector.uuid),
                parameters=connector.parameters_exclude_none(),
            ),
        )

        return Source.parse_obj(source.dict())

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "Source":
        """Gets a specific source by its identifier."""
        source = get_source.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), uuid=str(to_uuid(uuid))
        )

        return Source.parse_obj(source.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["Source"]:
        """Gets all sources by project."""
        raise NotImplementedError()

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        connector: OptionalArgument[SourceConnector] = UNSET,
        description: OptionalArgument[str] = UNSET,
    ) -> "Source":
        """Updates source."""
        parameters = connector.parameters_exclude_none() if isinstance(connector, SourceConnector) else UNSET
        source_update: Dict[str, Any] = dict(
            object="Node",
            type="Source",
            title=title,
            connector_uuid=str(connector.uuid) if isinstance(connector, SourceConnector) else UNSET,
            parameters=parameters,
            description=description,
        )

        source = update_source.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=SourceUpdate.parse_obj(drop_unset_values(source_update)),
        )

        return Source.parse_obj(source.dict())
