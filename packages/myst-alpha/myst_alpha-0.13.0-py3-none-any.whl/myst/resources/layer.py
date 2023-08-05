from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.timing import to_timing_create
from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.models.timing import AbsoluteOrRelativeTiming, TimeRangeBoundary, from_time_range_boundary
from myst.models.types import UNSET, ItemOrSlice, OptionalArgument, Unset, UUIDOrStr
from myst.openapi.api.projects.time_series.layers import (
    create_time_series_layer,
    get_time_series_layer,
    list_time_series_layers,
    update_time_series_layer,
)
from myst.openapi.models.layer_create import LayerCreate
from myst.openapi.models.layer_update import LayerUpdate
from myst.resources.edge import Edge

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.node import Node
    from myst.resources.project import Project
    from myst.resources.time_series import TimeSeries


class TimeSeriesLayer(Edge):
    """An edge into a time series.

    Time series layers are a way of stitching together data from multiple upstream nodes into a single, cohesive time
    series. Data can be combined across different time ranges, and a time series can use data from a lower-precedence
    layer when data is missing from a higher-precedence layer.

    Attributes:
        order: integer specifying priority of this layer when combining multiple layers; lower order implies higher
            precedence
        start_timing: the beginning of the natural time range this layer should produce data for; if None, there is no
            restriction on the beginning of the range
        end_timing: the end of the natural time range this layer should produce data for; if None, there is no
            restriction on the end of the range
    """

    order: int
    start_timing: Optional[AbsoluteOrRelativeTiming] = None
    end_timing: Optional[AbsoluteOrRelativeTiming] = None

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        time_series: Union["TimeSeries", UUIDOrStr],
        node: Union["Node", UUIDOrStr],
        order: int,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
    ) -> "TimeSeriesLayer":
        """Creates a layer into this time series."""
        layer = create_time_series_layer.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
            json_body=LayerCreate(
                object="Edge",
                type="Layer",
                upstream_node=str(get_resource_uuid(node)),
                order=order,
                output_index=output_index,
                label_indexer=label_indexer,
                start_timing=to_timing_create(from_time_range_boundary(start_timing)),
                end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            ),
        )

        return TimeSeriesLayer.parse_obj(dict(layer.dict(), project=get_resource_uuid(project)))

    @classmethod
    def get(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr], uuid: UUIDOrStr
    ) -> "TimeSeriesLayer":
        """Gets a specific layer by its identifier."""
        layer = get_time_series_layer.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
            uuid=str(uuid),
        )

        return TimeSeriesLayer.parse_obj(dict(layer.dict(), project=get_resource_uuid(project)))

    @classmethod
    def list(
        cls, project: Union["Project", UUIDOrStr], time_series: Union["TimeSeries", UUIDOrStr]
    ) -> List["TimeSeriesLayer"]:
        """Lists all layers for specified time series."""
        layers = list_time_series_layers.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
            time_series_uuid=str(get_resource_uuid(time_series)),
        )

        # Parse the layers into their final representation.
        unsorted_layers = [
            TimeSeriesLayer.parse_obj(dict(layer.dict(), project=get_resource_uuid(project))) for layer in layers.data
        ]

        # The API returns the layers ordered by create time, descending. We prefer explicit layer ordering here.
        return sorted(unsorted_layers, key=lambda layer: layer.order)

    def update(
        self,
        node: OptionalArgument[Union["Node", UUIDOrStr]] = UNSET,
        order: OptionalArgument[int] = UNSET,
        output_index: OptionalArgument[int] = UNSET,
        label_indexer: OptionalArgument[ItemOrSlice] = UNSET,
        start_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
        end_timing: OptionalArgument[TimeRangeBoundary] = UNSET,
    ) -> "TimeSeriesLayer":
        """Updates layer."""
        layer_update: Dict[str, Any] = dict(
            object="Edge",
            type="Layer",
            upstream_node=node if node is None or isinstance(node, Unset) else str(get_resource_uuid(node)),
            order=order,
            output_index=output_index,
            label_indexer=label_indexer,
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
        )

        layer = update_time_series_layer.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            time_series_uuid=str(self.downstream_node),
            uuid=str(self.uuid),
            json_body=LayerUpdate.parse_obj(drop_unset_values(layer_update)),
        )

        return TimeSeriesLayer.parse_obj(dict(layer.dict(), project=self.project))
