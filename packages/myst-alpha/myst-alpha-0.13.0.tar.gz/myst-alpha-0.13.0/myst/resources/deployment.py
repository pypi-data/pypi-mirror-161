from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from myst import get_client
from myst.adapters.utils import get_resource_uuid
from myst.core.time.time import Time
from myst.models.types import UUIDOrStr
from myst.openapi.api.projects.deployments import (
    create_project_deployment,
    deactivate_project_deployment,
    list_project_deployments,
)
from myst.openapi.models.deployment_create import DeploymentCreate
from myst.resources.resource import Resource

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Deployment(Resource):
    """A particular deployment of a project.

    A deployment is "active" if its `activate_time` is not `None` and its `deactivate_time` is `None`.

    Attributes:
        title: the title of the deployment.
        project: the identifier of the project with which the deployment is associated.
        activate_time: the time at which the deployment was activated, if any.
        deactive_time: the time at which the deployment was deactivated, if any.
    """

    title: str
    project: UUID
    activate_time: Optional[Time] = None
    deactivate_time: Optional[Time] = None

    @classmethod
    def create(cls, project: Union["Project", UUIDOrStr], title: str) -> "Deployment":
        """Creates a deployment for the project.

        Args:
            project: the project in which to create the deployment
            title: the title for the deployment

        Returns:
            the newly created deployment
        """
        deployment = create_project_deployment.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            json_body=DeploymentCreate(object="Deployment", title=title),
        )

        return Deployment.parse_obj(dict(deployment.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "Deployment":
        """Gets a specific deployment by its identifier."""
        deployments = cls.list(project)
        deployment = next((deployment for deployment in deployments if str(deployment.uuid) == str(uuid)), None)

        if deployment is None:
            raise ValueError(f"The deployment with {str(uuid)} can not found.")

        return deployment

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["Deployment"]:
        """Lists all deployments for specified project."""
        deployments = list_project_deployments.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project))
        )

        return [
            Deployment.parse_obj(dict(deployment.dict(), project=get_resource_uuid(project)))
            for deployment in deployments.data
        ]

    def deactivate(self) -> None:
        """Deactivate the deployment."""
        deployment = deactivate_project_deployment.request_sync(
            client=get_client(), project_uuid=str(self.project), uuid=str(self.uuid)
        )

        self.deactivate_time = Deployment.parse_obj(dict(deployment.dict(), project=self.project)).deactivate_time

    @property
    def is_active(self) -> bool:
        """Returns whether or not this deployment is active."""
        return self.deactivate_time is None
