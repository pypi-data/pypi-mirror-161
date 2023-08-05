from typing import Any, Dict, Optional, Union

from myst.client import Client
from myst.openapi.models.connector_type import ConnectorType
from myst.openapi.models.polymorphic_connector_list import PolymorphicConnectorList

from ...types import UNSET, Unset


def request_sync(client: Client, type: Optional[ConnectorType] = None) -> PolymorphicConnectorList:
    """Lists all connectors or a specified type of connectors."""

    json_type: Union[Unset, None, str] = UNSET
    if not isinstance(type, Unset):
        json_type = type.value if type else None

    params: Dict[str, Any] = {"type": json_type}
    params = {k: v for k, v in params.items() if v is not None}

    return client.request(method="get", path=f"/connectors/", response_class=PolymorphicConnectorList, params=params)
