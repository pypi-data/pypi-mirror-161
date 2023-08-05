from typing import TYPE_CHECKING, Optional
from uuid import UUID

from myst.client import get_client
from myst.core.time.time_delta import TimeDelta
from myst.models.enums import DeployStatus
from myst.models.timing import TimeRangeBoundary
from myst.models.types import AxisLabels, CoordinateLabels, ItemOrSlice, Shape
from myst.openapi.api.projects.time_series import create_time_series
from myst.openapi.models.time_series_create import TimeSeriesCreate
from myst.openapi.models.time_series_get import TimeSeriesGet
from myst.resources.resource import ShareableResource

if TYPE_CHECKING:
    from myst.resources.time_series import TimeSeries


class Node(ShareableResource):
    """A node in a project graph.

    Attributes:
        project: identifier of the project to which this node belongs
        title: the title of this node
        description: a brief description of the node
        deploy_status: whether this node is new, deployed, or inactive
    """

    project: UUID
    title: str
    description: Optional[str] = None
    deploy_status: DeployStatus

    def create_time_series(
        self,
        title: str,
        sample_period: TimeDelta,
        cell_shape: Shape = (),
        coordinate_labels: CoordinateLabels = (),
        axis_labels: AxisLabels = (),
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        description: Optional[str] = None,
    ) -> "TimeSeries":
        """Creates a single-layer time series downstream from this node.

        This method creates a time series and by a single layer whose downstream node is the newly created time series
        and whose upstream node is this node. Useful when creating a trivial time series just to capture the output of
        this node.

        Args:
            title: the title of the time series to create
            sample_period: the frequency at which the data is sampled
            cell_shape: the shape of the data in each cell
            coordinate_labels: the labels for each coordinate of a cell
            axis_labels: the labels for each axis of a cell
            output_index: which time dataset, out of the sequence of this node's time datasets, to pass to the layer
            label_indexer: the slice of this node's output data to pass into the layer
            start_timing: the beginning of the natural time range the layer should produce data for; if None, there is
                no restriction on the beginning of the range
            end_timing: the end of the natural time range the layer should produce data for; if None, there is no
                restriction on the end of the range
            description: a brief description of the time series

        Returns:
            the newly created time series
        """
        # Avoid circular imports.
        from myst.resources.time_series import TimeSeries

        time_series_get: TimeSeriesGet = create_time_series.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            json_body=TimeSeriesCreate(
                object="Node",
                type="TimeSeries",
                title=title,
                sample_period=sample_period.to_iso_string(),
                cell_shape=cell_shape,
                coordinate_labels=coordinate_labels,
                axis_labels=axis_labels,
                description=description,
            ),
        )

        time_series = TimeSeries.parse_obj(time_series_get.dict())

        time_series.create_layer(
            node=self,
            order=0,
            output_index=output_index,
            label_indexer=label_indexer,
            start_timing=start_timing,
            end_timing=end_timing,
        )

        return time_series
