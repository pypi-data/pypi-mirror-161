from typing import TYPE_CHECKING, List, Union
from uuid import UUID

from myst.adapters.utils import get_resource_uuid

from myst.client import get_client
from myst.models.types import UUIDOrStr, to_uuid
from myst.openapi.api.projects.hpos.jobs import get_hpo_job, list_hpo_jobs
from myst.openapi.models.hpo_job_state import HPOJobState
from myst.resources.resource import Resource

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.hpo import HPO
    from myst.resources.project import Project


class HPOJob(Resource):

    hpo: UUID
    state: HPOJobState
    num_trials_completed: int

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], hpo: Union["HPO", UUIDOrStr], uuid: UUIDOrStr) -> "HPOJob":
        """Gets a specific HPO job by its identifier."""
        hpo_job = get_hpo_job.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            hpo_uuid=str(get_resource_uuid(hpo)),
            uuid=str(to_uuid(uuid)),
        )

        return HPOJob.parse_obj(hpo_job.dict())

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr], hpo: Union["HPO", UUIDOrStr]) -> List["HPOJob"]:
        """Lists all jobs for the HPO."""
        hpo_jobs = list_hpo_jobs.request_sync(client=get_client(), project_uuid=str(get_resource_uuid(project)))

        return [
            HPOJob.parse_obj(hpo_job) for hpo_job in hpo_jobs.data if str(hpo_job.hpo) == str(get_resource_uuid(hpo))
        ]

    def is_completed(self) -> bool:
        """Returns `True` if the job has completed.

        Completed jobs include both successful and failed jobs.

        Returns:
            whether the job has completed
        """
        return self.state in [HPOJobState.SUCCESS, HPOJobState.FAILURE]
