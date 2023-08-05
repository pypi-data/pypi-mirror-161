from typing import Any, Dict

from myst.client import Client
from myst.openapi.models.hpo_result_list import HPOResultList


def request_sync(client: Client, project_uuid: str, hpo_uuid: str, job_uuid: str) -> HPOResultList:
    """Filters for HPO results associated with a specific job."""

    params: Dict[str, Any] = {"job_uuid": job_uuid}
    params = {k: v for k, v in params.items() if v is not None}

    return client.request(
        method="get",
        path=f"/projects/{project_uuid}/hpos/{hpo_uuid}/results/",
        response_class=HPOResultList,
        params=params,
    )
