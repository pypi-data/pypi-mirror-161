from myst.client import Client
from myst.openapi.models.project_node_policy_list import ProjectNodePolicyList


def request_sync(client: Client, project_uuid: str) -> ProjectNodePolicyList:
    """Lists all policies for a project."""

    return client.request(
        method="get", path=f"/projects/{project_uuid}/nodes/-/policies/", response_class=ProjectNodePolicyList
    )
