from typing import Any, Dict
from uuid import UUID

from myst.resources.node import Node


class ConnectorNode(Node):
    """A node backed by a connector.

    Attributes:
        connector_uuid: the UUID of the connector underlying this node
        parameters: the parameters to apply to the connector underlying this node
    """

    connector_uuid: UUID
    parameters: Dict[str, Any]
