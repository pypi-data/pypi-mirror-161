from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from myst.adapters.utils import drop_unset_values, get_resource_uuid
from myst.client import get_client
from myst.core.data.time_array import TimeArray
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.time_dataset import TimeDataset, TimeDatasetRow
from myst.models.timing import ScheduleTiming, TimeRangeBoundary
from myst.models.types import (
    UNSET,
    AxisLabels,
    CoordinateLabels,
    ItemOrSlice,
    OptionalArgument,
    Shape,
    Unset,
    UUIDOrStr,
    to_uuid,
)
from myst.openapi.api.projects.time_series import (
    create_time_series,
    get_time_series,
    insert_time_series_data,
    list_all_time_series,
    query_time_series_data,
    update_time_series,
)
from myst.openapi.models.time_series_create import TimeSeriesCreate
from myst.openapi.models.time_series_insert import TimeSeriesInsert
from myst.openapi.models.time_series_update import TimeSeriesUpdate
from myst.resources.layer import TimeSeriesLayer
from myst.resources.node import Node
from myst.resources.policy import TimeSeriesRunPolicy
from myst.resources.result import TimeSeriesRunResult, TimeSeriesRunResultMetadata

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.recipes.time_series_recipe import TimeSeriesRecipe
    from myst.resources.project import Project


class TimeSeries(Node):
    """A queryable, shareable node containing fixed-frequency, arbitrarily dimensioned time series data.

    A time series stitches together data from multiple layers into a single stream, by consuming data from lower-
    precedence layers when data from higher-precedence layers is not available, and by consuming only the upstream data
    that is within the time range bounds set on each layer.

    In addition to queries, a time series also supports inserts, which take precedence over data flowing through the
    input layers.

    Attributes:
        sample_period: the frequency at which the data is sampled
        cell_shape: the shape of the data in each cell
        coordinate_labels: the labels for each coordinate of a cell
        axis_labels: the labels for each axis of a cell
    """

    sample_period: TimeDelta
    cell_shape: Shape
    coordinate_labels: CoordinateLabels
    axis_labels: AxisLabels

    @classmethod
    def create(
        cls,
        project: Union["Project", UUIDOrStr],
        title: str,
        sample_period: TimeDelta,
        cell_shape: Shape = (),
        coordinate_labels: CoordinateLabels = (),
        axis_labels: AxisLabels = (),
        description: Optional[str] = None,
    ) -> "TimeSeries":
        """Creates a new time series node.

        Args:
            project: the project in which to create the time series
            title: the title of the time series
            sample_period: the frequency at which the data is sampled
            cell_shape: the shape of the data in each cell of the time series
            coordinate_labels: the labels for each coordinate of a cell in the time series
            axis_labels: the labels for each axis of a cell in the time series
            description: a brief description of the time series

        Returns:
            the newly created time series
        """
        time_series = create_time_series.request_sync(
            client=get_client(),
            project_uuid=str(get_resource_uuid(project)),
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

        return TimeSeries.parse_obj(time_series.dict())

    @classmethod
    def create_from_recipe(
        cls,
        project: Union["Project", UUIDOrStr],
        recipe: "TimeSeriesRecipe",
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "TimeSeries":
        """Creates a new time series node based on a provided recipe.

        Args:
            project: the project in which to create the time series
            recipe: the recipe used to create the time series
            title: the title of the time series; if none is given, the recipe will supply a sensible default
            description: the description of the time series

        Returns:
            the newly created time series
        """
        return recipe.create(project=project, title=title, description=description)

    @classmethod
    def get(cls, project: Union["Project", UUIDOrStr], uuid: UUIDOrStr) -> "TimeSeries":
        """Gets a specific time series by its identifier."""
        time_series = get_time_series.request_sync(
            client=get_client(), project_uuid=str(get_resource_uuid(project)), uuid=str(to_uuid(uuid))
        )

        return TimeSeries.parse_obj(time_series.dict())

    def insert_time_array(self, time_array: TimeArray) -> None:
        """Inserts data from a `TimeArray` into this time series.

        The data from this manual insertion will take precedence over the other layers flowing into this time series.

        Args:
            time_array: the array of data to be inserted
        """
        time_dataset_row = TimeDatasetRow(
            start_time=time_array.start_time,
            end_time=time_array.end_time,
            as_of_time=time_array.as_of_time,
            values=time_array.values,
            mask=time_array.mask,
        )

        time_dataset = TimeDataset(
            object="TimeDataset",
            cell_shape=time_array.cell_shape,
            sample_period=time_array.sample_period,
            data=[time_dataset_row],
            coordinate_labels=time_array.coordinate_labels,
            axis_labels=time_array.axis_labels,
        )

        insert_time_series_data.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=TimeSeriesInsert(time_dataset=time_dataset),
        )

    @classmethod
    def list(cls, project: Union["Project", UUIDOrStr]) -> List["TimeSeries"]:
        """Gets all time series by project."""
        all_time_series = list_all_time_series.request_sync(client=get_client())

        return [
            TimeSeries.parse_obj(time_series.dict())
            for time_series in all_time_series.data
            if str(time_series.project) == str(get_resource_uuid(project))
        ]

    def update(
        self,
        title: OptionalArgument[str] = UNSET,
        sample_period: OptionalArgument[TimeDelta] = UNSET,
        cell_shape: OptionalArgument[Shape] = UNSET,
        coordinate_labels: OptionalArgument[CoordinateLabels] = UNSET,
        axis_labels: OptionalArgument[AxisLabels] = UNSET,
        description: OptionalArgument[str] = UNSET,
    ) -> "TimeSeries":
        """Updates time series."""
        time_series_update: Dict[str, Any] = dict(
            object="Node",
            type="TimeSeries",
            title=title,
            sample_period=sample_period.to_iso_string() if isinstance(sample_period, TimeDelta) else sample_period,
            cell_shape=cell_shape,
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
            description=description,
        )

        time_series = update_time_series.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            json_body=TimeSeriesUpdate.parse_obj(drop_unset_values(time_series_update)),
        )

        return TimeSeries.parse_obj(time_series.dict())

    def query_time_array(
        self,
        start_time: Time,
        end_time: Time,
        as_of_time: Optional[Time] = None,
        as_of_offset: Optional[TimeDelta] = None,
    ) -> TimeArray:
        """Queries this time series for data according to the given parameters.

        At most one of `as_of_time` and `as_of_offset` may be specified. If `as_of_time` is specified, the query will
        return data as of that particular time. If `as_of_offset` is specified, the query will return data for a
        constant offset between the "natural" time and the as of time. If neither is specified, the API assumes an
        `as_of_time` of now.

        Args:
            start_time: the beginning of the natural time range to query over, inclusive
            end_time: the end of the natural time range to query over, exclusive
            as_of_time: the precise as of time to query
            as_of_offset: the offset from as of time to query by, where as_of_offset = natural_time - as_of_time

        Returns:
            a time array containing data for the specified time range and as of time

        Raises:
            ValueError: if both `as_of_time` and `as_of_offset` are specified
        """
        if as_of_time and as_of_offset:
            raise ValueError("At most one of `as_of_time` and `as_of_offset` may be specified.")

        time_series_query_result_get = query_time_series_data.request_sync(
            client=get_client(),
            project_uuid=str(self.project),
            uuid=str(self.uuid),
            start_time=start_time.to_iso_string(),
            end_time=end_time.to_iso_string(),
            as_of_time=as_of_time.to_iso_string() if as_of_time is not None else None,
            as_of_offset=as_of_offset.to_iso_string() if as_of_offset is not None else None,
        )

        time_dataset = TimeDataset.parse_obj(time_series_query_result_get.time_dataset)

        return time_dataset.flatten()

    def create_layer(
        self,
        node: Union[Node, UUIDOrStr],
        order: int,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
    ) -> TimeSeriesLayer:
        """Creates a layer into this time series.

        Args:
            node: the node whose data will flow into this time series
            order: integer specifying priority of this layer when combining multiple layers; lower order implies
                higher precedence
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this time
                series
            label_indexer: the slice of the upstream data to pass to this time series
            start_timing: the beginning of the natural time range this layer should produce data for; if None, there
                is no restriction on the beginning of the range
            end_timing: the end of the natural time range this layer should produce data for; if None, there is no
                restriction on the end of the range

        Returns:
            the newly created time series layer
        """
        return TimeSeriesLayer.create(
            project=self.project,
            time_series=self.uuid,
            node=node,
            order=order,
            output_index=output_index,
            label_indexer=label_indexer,
            start_timing=start_timing,
            end_timing=end_timing,
        )

    def list_layers(self) -> List[TimeSeriesLayer]:
        """Lists all layers into this time series."""
        return TimeSeriesLayer.list(project=self.project, time_series=self)

    def create_run_policy(
        self,
        schedule_timing: Union[Time, TimeDelta, ScheduleTiming],
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        active: bool = True,
    ) -> TimeSeriesRunPolicy:
        return TimeSeriesRunPolicy.create(
            project=self.project,
            time_series=self.uuid,
            schedule_timing=schedule_timing,
            start_timing=start_timing,
            end_timing=end_timing,
            active=active,
        )

    def list_run_policies(self) -> List[TimeSeriesRunPolicy]:
        return TimeSeriesRunPolicy.list(project=self.project, time_series=self.uuid)

    def list_run_results(self) -> List[TimeSeriesRunResultMetadata]:
        return TimeSeriesRunResult.list(project=self.project, time_series=self)

    def get_run_result(self, time_series_result: Union[TimeSeriesRunResultMetadata, UUIDOrStr]) -> TimeSeriesRunResult:
        return TimeSeriesRunResult.get(
            project=self.project, time_series=self, uuid=get_resource_uuid(time_series_result)
        )
