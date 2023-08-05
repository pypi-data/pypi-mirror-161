from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from pydantic import Field, root_validator, validator
from pydantic.typing import Literal

from myst.core.data.time_array import TimeArray
from myst.core.data.validators import (
    check_arrays_same_length_as_time_range,
    ensure_not_none,
    maybe_to_boolean_int_array,
    to_numpy_float_array,
)
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.base_model import BaseModel
from myst.models.types import AxisLabels, CoordinateLabels, Metadata, Shape


def _validate_time_array_compatibility(time_arrays: Iterable[TimeArray], check_shape: Optional[bool] = True) -> None:
    """Validates that the passed time arrays are compatible.

    Args:
        time_arrays: time arrays to validate
        check_shape: flag to indicate if we should check the time array shapes are equal

    Raises:
        ValueError: if the passed time arrays are incompatible
    """
    # Validate that the sample periods are the same across all time arrays.
    sample_period = None
    for time_array in time_arrays:
        if sample_period is not None:
            if time_array.sample_period != sample_period:
                raise ValueError("Time arrays do not share the same sample period.")
        else:
            sample_period = time_array.sample_period

    # Validate that the cell shapes are the same across all time arrays.
    cell_shape = None
    for time_array in time_arrays:
        if cell_shape is not None:
            if time_array.cell_shape != cell_shape:
                raise ValueError("Time arrays do not share the same cell shape.")
        else:
            cell_shape = time_array.cell_shape

    # Validate that the coordinate labels are the same across all time arrays.
    coordinate_labels = None
    for time_array in time_arrays:
        if coordinate_labels is not None:
            if not np.array_equal(time_array.coordinate_labels, coordinate_labels):
                raise ValueError("Time arrays do not share the same coordinate labels.")
        else:
            coordinate_labels = time_array.coordinate_labels

    # Validate that the axis labels are the same across all time arrays.
    axis_labels = None
    for time_array in time_arrays:
        if axis_labels is not None:
            if not np.array_equal(time_array.axis_labels, axis_labels):
                raise ValueError("Time arrays do not share the same axis labels.")
        else:
            axis_labels = time_array.axis_labels

    if check_shape:
        # Validate that the shapes are the same across all time arrays.
        shape = None
        for time_array in time_arrays:
            if shape is not None:
                if time_array.shape != shape:
                    raise ValueError("Time arrays do not share the same shape.")
            else:
                shape = time_array.shape


class TimeDatasetRow(BaseModel):
    start_time: Time = Field(
        ..., description="The time at which this time series data starts, inclusive.", example="2021-01-01T01:23:45Z"
    )
    end_time: Time = Field(
        ..., description="The time at which this time series data ends, exclusive.", example="2021-02-01T12:34:56Z"
    )
    as_of_time: Time = Field(
        ..., description="The time as of which this time series data was known.", example="2021-06-01T00:00:00Z"
    )
    values: np.ndarray = Field(
        ...,
        description="The multidimensional array of values for this time series.",
        examples=dict(
            empty=dict(summary="Empty array", value=[]),
            vector=dict(summary="1-D array of floats", value=[1.0, -47.47]),
            matrix=dict(summary="2-D array of floats", value=[[1.1, 1.2], [2.1, 2.2]]),
        ),
    )
    mask: Optional[np.ndarray] = Field(
        None,
        description=(
            "The mask to be used to filter out invalid or missing data. Must have the same shape as `values`, and each "
            "mask value must be either 0 or 1."
        ),
        examples=dict(
            empty=dict(summary="Empty array", value=[]),
            vector=dict(summary="1-D array of ints", value=[1, 0]),
            matrix=dict(summary="2-D array of ints", value=[[1, 0], [0, 1]]),
        ),
    )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Returns the dictionary representation of this `TimeDatasetRow`."""
        dict_repr = super().dict(*args, **kwargs)

        arr: np.ndarray = dict_repr["values"]
        dict_repr["values"] = np.where(np.isnan(arr), None, arr).tolist()

        if self.mask is not None:
            dict_repr["mask"] = dict_repr["mask"].tolist()

        return dict_repr

    _ensure_values_not_none = validator("values", pre=True, allow_reuse=True)(ensure_not_none)
    _coerce_values_to_float_array = validator("values", pre=True, allow_reuse=True)(to_numpy_float_array)

    _coerce_mask_to_boolean_int_array = validator("mask", pre=True, allow_reuse=True)(maybe_to_boolean_int_array)

    class Config:
        # Allow arbitrary types in order to support `np.ndarray` directly.
        arbitrary_types_allowed = True


class TimeDataset(BaseModel):
    object: Literal["TimeDataset"] = Field(
        example="TimeDataset",
        description="The field representing the type of object this resource is. Must be `TimeDataset`.",
    )
    coordinate_labels: Optional[CoordinateLabels] = Field(
        example=("field",), description="The labels for each coordinate of a cell in the time dataset."
    )
    axis_labels: Optional[AxisLabels] = Field(
        example=(), description="The labels for each axis of a cell in the time dataset."
    )
    sample_period: TimeDelta = Field(
        example="PT1H", description="The sample period of the time dataset formatted as an ISO 8601 Duration string."
    )
    metadata: Optional[Metadata] = Field(
        None, example={"key": "value"}, description="User-defined metadata about the time dataset."
    )
    data: List[TimeDatasetRow] = Field(description="List of rows belonging to this time dataset.", min_items=1)
    cell_shape: Optional[Shape] = Field(example=(), description="The shape of each cell in the time dataset.")

    @validator("data")
    def ensure_unique_as_of_times(cls, v: List[TimeDatasetRow]) -> List[TimeDatasetRow]:
        as_of_times = [row.as_of_time for row in v]
        if len(set(as_of_times)) != len(as_of_times):
            raise ValueError("The `as_of_time` for each `TimeDatasetRow` must be unique.")

        return v

    @validator("data")
    def check_cell_shapes_equal(cls, v: List[TimeDatasetRow]) -> List[TimeDatasetRow]:
        if len(set([row.values.shape[1:] for row in v])) > 1:
            raise ValueError("The cell shape of `values` in each `TimeDatasetRow` must match.")

        return v

    @validator("data")
    def sort_rows_by_as_of_time_desc(cls, v: List[TimeDatasetRow]) -> List[TimeDatasetRow]:
        return sorted(v, key=lambda row: row.as_of_time, reverse=True)

    @validator("cell_shape", always=True)
    def infer_cell_shape_from_data(cls, v: Any, values: Dict[str, Any]) -> Any:
        data = values.get("data", None)

        # We rely on previous validation to ensure that each row has the same cell shape.
        if v is None and data is not None and len(data):
            return data[0].values.shape[1:]

        return v

    @root_validator
    def validate_time_range_consistent_with_values(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validates that the given time range is consistent with the values and mask."""
        sample_period = values.get("sample_period", None)

        if sample_period is not None:
            for row in values.get("data", ()):
                if row.start_time and row.end_time and row.values is not None:
                    check_arrays_same_length_as_time_range(
                        start_time=row.start_time,
                        end_time=row.end_time,
                        sample_period=sample_period,
                        values=row.values,
                        mask=row.mask,
                    )

        return values

    @classmethod
    def from_time_arrays(cls, time_arrays: Sequence[TimeArray]) -> "TimeDataset":
        if not time_arrays:
            raise ValueError("Cannot construct `TimeDataset` from empty collection.")

        _validate_time_array_compatibility(time_arrays=time_arrays, check_shape=False)

        first_time_array = time_arrays[0]

        time_dataset_rows = [
            TimeDatasetRow(
                start_time=time_array.start_time,
                end_time=time_array.end_time,
                as_of_time=time_array.as_of_time,
                values=time_array.values,
                mask=time_array.mask,
            )
            for time_array in time_arrays
        ]

        return TimeDataset(
            object="TimeDataset",
            cell_shape=first_time_array.cell_shape,
            sample_period=first_time_array.sample_period,
            data=time_dataset_rows,
            coordinate_labels=first_time_array.coordinate_labels,
            axis_labels=first_time_array.axis_labels,
        )

    def to_time_arrays(self) -> List[TimeArray]:
        """Returns the data in this time dataset as a list of time arrays."""
        return [
            TimeArray(
                sample_period=self.sample_period,
                start_time=time_dataset_row.start_time,
                end_time=time_dataset_row.end_time,
                as_of_time=time_dataset_row.as_of_time,
                values=time_dataset_row.values,
                mask=time_dataset_row.mask,
                coordinate_labels=self.coordinate_labels,
                axis_labels=self.axis_labels,
            )
            for time_dataset_row in self.data
        ]

    def flatten(self) -> TimeArray:
        """Flattens the time dataset by the latest as of time and returns a single time array.

        Deduplication happens by always prioritizing values of the latest as of time for each natural time.

        Note that missing values in the resulting time array will be masked using the `mask` attribute.

        Returns:
            flattened time array
        """
        time_arrays = self.to_time_arrays()

        # Special-case the common situation where the time dataset trivially reduces to a single time array.
        if len(time_arrays) == 1:
            return time_arrays[0]

        # Extract the pandas objects for the `values` and `mask` from the underlying time arrays.
        values_pandas_objects, mask_pandas_objects = {}, {}
        for time_array in self.to_time_arrays():
            values_pandas_object = time_array.to_pandas_object(apply_mask=False)
            values_pandas_objects.update({time_array.as_of_time.to_pandas_timestamp(): values_pandas_object})
            mask_pandas_object = values_pandas_object.copy()
            mask = (
                time_array.mask
                if time_array.mask is not None
                else np.zeros(shape=values_pandas_object.shape, dtype=int)
            )
            mask_pandas_object.values[:] = mask.reshape(mask_pandas_object.shape)
            mask_pandas_objects.update({time_array.as_of_time.to_pandas_timestamp(): mask_pandas_object})

        # Concatenate the extracted pandas objects across both dimensions.
        concat_values_pandas_object = pd.concat(values_pandas_objects, axis=0).sort_index()
        concat_mask_pandas_object = pd.concat(mask_pandas_objects, axis=0).sort_index()
        concat_combined_pandas_object = pd.concat([concat_values_pandas_object, concat_mask_pandas_object], axis=1)

        # Extract the time, as of time, and as of offset indexes.
        time_index = concat_values_pandas_object.index.get_level_values(level=1)
        as_of_time_index = concat_values_pandas_object.index.get_level_values(level=0)

        # Apply the boolean filter and deduplicate the time index based on the last row in each group.
        concat_combined_pandas_object = concat_combined_pandas_object.set_index(time_index)
        combined_pandas_object = concat_combined_pandas_object.groupby(concat_combined_pandas_object.index).last()

        # Ensure that the datetime index of the resulting pandas object is uniformly sampled.
        pandas_datetime_index = pd.date_range(
            start=combined_pandas_object.index.min(),
            end=combined_pandas_object.index.max() + self.sample_period.to_pandas_date_offset(),
            freq=self.sample_period.to_pandas_frequency(),
            name="time",
            closed="left",
            tz="UTC",
        )
        combined_pandas_object = combined_pandas_object.reindex(pandas_datetime_index)

        # Extract the pandas object and mask from the combined pandas object.
        num_values_columns = int(np.prod(self.cell_shape))
        values_pandas_object = combined_pandas_object.iloc[:, :num_values_columns]
        mask_pandas_object = combined_pandas_object.iloc[:, num_values_columns:].fillna(value=1)
        mask = mask_pandas_object.values.astype(int).reshape(-1, *self.cell_shape)

        # Extract the most recent as of time from the underlying time arrays.
        as_of_time = Time(as_of_time_index.max())

        if self.cell_shape == ():
            values_pandas_object = values_pandas_object.iloc[:, 0]

        return TimeArray.from_pandas_object(pandas_object=values_pandas_object, as_of_time=as_of_time, mask=mask)
