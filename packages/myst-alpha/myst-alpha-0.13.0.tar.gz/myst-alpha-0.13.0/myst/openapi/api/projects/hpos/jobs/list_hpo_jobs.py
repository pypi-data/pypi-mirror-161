from myst.client import Client
from myst.openapi.models.hpo_job_get_list import HPOJobGetList


def request_sync(client: Client, project_uuid: str) -> HPOJobGetList:
    """Lists all HPO jobs for the project."""

    return client.request(method="get", path=f"/projects/{project_uuid}/hpos/-/jobs/", response_class=HPOJobGetList)
