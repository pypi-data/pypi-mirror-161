from myst.client import Client
from myst.openapi.models.project_node_job_list import ProjectNodeJobList


def request_sync(client: Client, project_uuid: str) -> ProjectNodeJobList:
    """Lists jobs."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/nodes/-/jobs/", response_class=ProjectNodeJobList
    )
