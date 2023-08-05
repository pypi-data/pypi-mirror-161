from myst.client import Client
from myst.openapi.models.hpo_job_get import HPOJobGet


def request_sync(client: Client, project_uuid: str, hpo_uuid: str, uuid: str) -> HPOJobGet:
    """Gets an hpo job for the project and specified hpo."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/hpos/{hpo_uuid}/jobs/{uuid}", response_class=HPOJobGet
    )
