from typing import Any, Dict, Optional

from myst.client import Client
from myst.openapi.models.user_list import UserList


def request_sync(client: Client, organization_uuid: Optional[str] = None) -> UserList:
    """Lists users."""

    params: Dict[str, Any] = {"organization_uuid": organization_uuid}
    params = {k: v for k, v in params.items() if v is not None}

    return client.request(method="get", path=f"/users/", response_class=UserList, params=params)
