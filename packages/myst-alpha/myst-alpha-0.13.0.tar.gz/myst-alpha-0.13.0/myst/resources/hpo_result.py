from typing import TYPE_CHECKING, Union
from uuid import UUID

from myst.adapters.utils import get_resource_uuid

from myst.client import get_client
from myst.models.types import UUIDOrStr
from myst.openapi.api.projects.hpos.results import get_hpo_result
from myst.resources.hpo_trial import HPOTrial
from myst.resources.resource import Resource

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.hpo import HPO
    from myst.resources.hpo_job import HPOJob
    from myst.resources.project import Project


class HPOResult(Resource):

    uuid: UUID
    best_trial: HPOTrial

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], hpo: Union["HPO", UUIDOrStr], job: Union["HPOJob", UUIDOrStr]
    ) -> "HPOResult":
        hpo_result_list = get_hpo_result.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            hpo_uuid=str(get_resource_uuid(hpo)),
            job_uuid=str(get_resource_uuid(job)),
        )

        return HPOResult.parse_obj(hpo_result_list.data[0].dict())
