from typing import Optional
from uuid import UUID

from myst.models.types import ItemOrSlice
from myst.resources.resource import Resource


class Edge(Resource):
    """An edge between two nodes in a project graph.

    Attributes:
        project: identifier of the project this edge belongs to
        upstream_node: the identifier of the node data flows into this edge from
        downstream_node: the identifier of the node data flows out of this edge to
        output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this edge
        label_indexer: the slice of the upstream data to pass to this edge
    """

    project: UUID
    upstream_node: UUID
    downstream_node: UUID
    output_index: int
    label_indexer: Optional[ItemOrSlice] = None
