from myst.client import Client
from myst.openapi.models.hpo_job_get import HPOJobGet


def request_sync(client: Client, project_uuid: str, uuid: str) -> HPOJobGet:
    """Runs an HPO job."""

    return client.request(method="post", path=f"/projects/{project_uuid}/hpos/{uuid}:run", response_class=HPOJobGet)
