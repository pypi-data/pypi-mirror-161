from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pydantic import Field, root_validator, validator

from myst.core.data.validators import (
    check_arrays_same_length_as_time_range,
    ensure_not_none,
    maybe_to_boolean_int_array,
    to_numpy_float_array,
)
from myst.core.time.time import Time, TimeDelta
from myst.models.base_model import BaseModel
from myst.models.types import AxisLabels, CoordinateLabels, ItemOrSlice, Shape

_TIME_INDEX_NAME = "time"


def _process_pandas_object(pandas_object: Union[pd.Series, pd.DataFrame]) -> Tuple[TimeDelta, Time, Time]:
    """Processes the time arguments when the passed data is a `pandas.Series` or `pandas.DataFrame`.

    Args:
        pandas_object: pandas series or data frame

    Returns:
        tuple of (sample period, start time, end time)

    Raises:
        ValueError: if index does not have a frequency or if the pandas object is empty
    """
    # Validate pandas object fulfills `TimeArray` requirements.
    if pandas_object.index.freq is None:
        raise ValueError("The frequency of the time index must be specified.")

    if pandas_object.empty:
        raise ValueError("Creating a time array from an empty Pandas object is not allowed.")

    sample_period = TimeDelta(pandas_object.index.freq)
    start_time = Time(pandas_object.index.min())
    end_time = Time(pandas_object.index.max() + sample_period.to_pandas_date_offset())

    return sample_period, start_time, end_time


def _compute_cell_shape(coordinate_labels: CoordinateLabels) -> Shape:
    """Computes the cell shape from the given coordinate labels.

    Args:
        coordinate_labels: coordinate labels to compute cell shape from

    Returns:
        computed cell shape
    """
    # The cell shape is computed based on the number of coordinates in each dimension.
    return tuple(map(len, coordinate_labels))


def _compute_coordinate_and_axis_labels_for_pandas_index(pandas_index: pd.Index) -> Tuple[CoordinateLabels, AxisLabels]:
    """Computes the coordinate and axis labels from a `pandas.Index`.

    This will typically be used to compute the coordinate and axis labels for a `pandas.DataFrame` given its `columns`
    index.

    Args:
        pandas_index: pandas index to compute the coordinate and axis labels from

    Returns:
        coordinate_labels: coordinate labels
        axis_labels: axis labels
    """
    coordinate_labels: CoordinateLabels = tuple(
        map(tuple, [pandas_index.unique(level=level).tolist() for level in range(pandas_index.nlevels)])
    )
    axis_labels = tuple(pandas_index.names)

    return coordinate_labels, axis_labels


def _get_axis_labels_to_collapse(indexer: ItemOrSlice, axis_labels: AxisLabels) -> AxisLabels:
    """Returns the axis labels that are indexed with scalar indexers, and therefore should be collapsed.

    Args:
        indexer: item or slice; if a tuple of items, one must be present for each axis in `axis_labels`
        axis_labels: axis labels identifying axis over which each item in `indexer` indexes into

    Returns:
        axis labels that were indexed with a scalar value, and therefore should be collapsed
    """
    return tuple(
        axis_label for sub_item, axis_label in zip(indexer, axis_labels) if isinstance(sub_item, (int, str))  # type: ignore
    )


def ndarray_to_list(a: np.ndarray) -> list:
    """Converts a numpy array to a json-serializable list."""
    return np.where(np.isnan(a), None, a).tolist() if a is not None else None


class TimeArray(BaseModel):
    class Config:
        # Allow arbitrary types in order to support `np.ndarray` directly.
        arbitrary_types_allowed = True
        json_encoders = {np.ndarray: ndarray_to_list}

    sample_period: TimeDelta
    start_time: Time
    end_time: Time
    as_of_time: Time
    values: np.ndarray
    mask: Optional[np.ndarray] = None
    coordinate_labels: CoordinateLabels = Field(None)
    axis_labels: AxisLabels = Field(None)

    _ensure_values_not_none = validator("values", pre=True, allow_reuse=True)(ensure_not_none)
    _coerce_values_to_float_array = validator("values", pre=True, allow_reuse=True)(to_numpy_float_array)

    _coerce_mask_to_boolean_int_array = validator("mask", pre=True, allow_reuse=True)(maybe_to_boolean_int_array)

    @validator("coordinate_labels", pre=True, always=True)
    def fill_in_coordinate_labels_if_none(cls, coordinate_labels: Any, values: Dict[str, Any]) -> Any:
        """Returns coordinate labels unchanged if not None, otherwise default integer-valued coordinate labels."""
        ndarray = values.get("values", None)

        if ndarray is not None and coordinate_labels is None:
            if len(ndarray.shape) > 1:
                return tuple([tuple(range(dim)) for dim in tuple(ndarray.shape[1:])])
            else:
                return ()

        return coordinate_labels

    @validator("coordinate_labels")
    def check_coordinate_labels(cls, coordinate_labels: CoordinateLabels, values: Dict[str, Any]) -> CoordinateLabels:
        """Checks that the coordinate labels are unique in each axis and compatible with cell shape of values."""
        ndarray = values.get("values", None)

        if coordinate_labels is not None and ndarray is not None:
            cell_shape = ndarray.shape[1:]
            coordinate_cell_shape = _compute_cell_shape(coordinate_labels=coordinate_labels)

            if cell_shape != coordinate_cell_shape:
                raise ValueError(f"Passed `coordinate_labels` are not compatible with cell shape of `{cell_shape}`.")

            if len(coordinate_cell_shape) > 0:
                if list(map(len, map(set, coordinate_labels))) != list(map(len, coordinate_labels)):  # type: ignore
                    raise ValueError("Passed `coordinate_labels` must contain only unique values across each axis.")

        return coordinate_labels

    @validator("axis_labels", pre=True, always=True)
    def fill_in_axis_labels_if_none(cls, axis_labels: Any, values: Dict[str, Any]) -> Any:
        """Returns axis labels unchanged if not None, otherwise default integer-valued coordinate labels."""
        ndarray = values.get("values", None)

        if ndarray is not None and axis_labels is None:
            if len(ndarray.shape) > 1:
                return tuple(range(len(ndarray.shape[1:])))
            else:
                return ()

        return axis_labels

    @validator("axis_labels")
    def check_axis_labels(cls, axis_labels: AxisLabels, values: Dict[str, Any]) -> AxisLabels:
        """Checks that the axis labels are unique and compatible with cell shape of values."""
        ndarray = values.get("values", None)

        if axis_labels is not None and ndarray is not None:
            cell_shape = ndarray.shape[1:]

            if len(cell_shape) != len(axis_labels):
                raise ValueError(f"Passed `axis_labels` are not compatible with cell shape of `{cell_shape}`.")

            if len(set(axis_labels)) != len(axis_labels):
                raise ValueError("Passed `axis_labels` must contain only unique values.")

        return axis_labels

    @root_validator
    def check_time_range_parameters(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_time: Optional[Time] = values.get("start_time", None)
        end_time: Optional[Time] = values.get("end_time", None)
        as_of_time: Optional[Time] = values.get("as_of_time", None)
        sample_period: Optional[TimeDelta] = values.get("sample_period", None)

        if start_time and end_time and as_of_time and sample_period:
            frequency = sample_period.to_pandas_frequency().freqstr
            for time in (start_time, end_time, as_of_time):
                timestamp = time.to_pandas_timestamp()
                if timestamp != timestamp.floor(frequency):
                    raise ValueError(f"Specified time `{time}` is not aligned with frequency `{frequency}`.")

        return values

    @root_validator
    def check_length_of_data_against_index(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_time: Optional[Time] = values.get("start_time", None)
        end_time: Optional[Time] = values.get("end_time", None)
        sample_period: Optional[TimeDelta] = values.get("sample_period", None)
        data: Optional[np.ndarray] = values.get("values", None)
        mask: Optional[np.ndarray] = values.get("mask", None)

        if start_time and end_time and sample_period and data is not None:
            check_arrays_same_length_as_time_range(
                start_time=start_time, end_time=end_time, sample_period=sample_period, values=data, mask=mask
            )

        return values

    @property
    def shape(self) -> Shape:
        """The shape of this time array, where the time axis is included as the first dimension."""
        return self.values.shape

    @property
    def cell_shape(self) -> Shape:
        """The shape of the data in this time array at a single timestamp."""
        return self.values.shape[1:]

    @property
    def empty(self) -> bool:
        """Returns True if this time array is empty, False otherwise."""
        return self.values.size == 0

    def __repr__(self) -> str:
        """Returns a representation of the underlying `pandas.Series` or `pandas.DataFrame`."""
        return repr(self.to_pandas_object())

    def __getitem__(self, item: ItemOrSlice) -> "TimeArray":
        """Gets an item or slice from the time array.

        Note that this method only support slicing on the `coordinate_labels`, so not on the time dimension. Time arrays
        with scalar data can never be sliced, since they have no coordinate labels.

        This method will not automatically apply the `mask` to the subset time array, but it will be propagated through
        appropriately in the `TimeArray.mask` attribute.

        The slicing behavior of this method diverges from the behavior of the `loc` method in `pandas` in certain cases.
        The `loc` method only collapses the axes if only scalar indexers are given (e.g. `("a", "z")`), whereas this
        method always collapses axes that correspond to scalar indexers.

        This difference is best illustrated by a few examples. Assume we have a `TimeArray` with the coordinate labels
        `(("a", "b"), ("x", "y", "z"))` and axis labels `("first", "second")`:

            * Indexing `["a"]` will result in the coordinate labels `("x", "y", "z")`. Note that the `"first"` axis is
              collapsed. The `loc` method in `pandas` behaves the same in this case.
            * Indexing `["a", "z"]` will result in the coordinate labels `()`. Note that both axes are collapsed. The
              `loc` method in `pandas` also behaves the same in this case.
            * Indexing using `["a", ["z"]]` – or more generally, including at least one non-scalar indexer – will result
              in the coordinate labels `(("z",),)`. Note that only the `"first"` axis is collapsed. The `loc` method in
              `pandas` *does not* behave the same in this case. Rather, it chooses to not collapse any axes and would
              return coordinate labels `("a", ("z",),)`. We found this behavior inconsistent and chose to improve upon
              it in this method.

        Args:
            item: item or slice

        Returns:
            resultant subset time array

        Raises:
            KeyError: if an invalid item for the time array's shape is given
        """
        if self.cell_shape == ():
            raise KeyError("Cannot slice a scalar time array.")

        # Convert `values` and `mask` `numpy.ndarray` objects into `pandas` objects to take advantage of advanced
        # multi-indexing support.
        subset_values_pandas_object = self.to_pandas_object(apply_mask=False).copy()

        # Note: For some reason, `pandas` will not let you use scalar indexers on a multi-index column with only one
        #   level, so convert the columns into a normal index before slicing into it.
        if len(self.cell_shape) == 1:
            subset_values_pandas_object.columns = subset_values_pandas_object.columns.get_level_values(0)

        # Leverage the already computed multi-index but fill it in with the `mask` data.
        subset_mask_pandas_object = subset_values_pandas_object.copy()
        subset_mask_pandas_object.values[:] = np.zeros(subset_mask_pandas_object.shape)
        if self.mask is not None:
            subset_mask_pandas_object.values[:] = self.mask.reshape(subset_mask_pandas_object.shape)

        # Perform the slice.
        subset_values_pandas_object = subset_values_pandas_object.loc[:, item]
        subset_mask_pandas_object = subset_mask_pandas_object.loc[:, item]

        # If the resultant `subset_values_pandas_object` is empty, that means no matches were found for the slice,
        # making it invalid.
        if subset_values_pandas_object.empty:
            raise KeyError(f"Invalid indexer: `{item}`.")

        # If multiple dimensions are specified and at least one non-scalar item was referenced, remove levels that were
        # referenced via scalar values.
        if isinstance(item, tuple):
            is_scalar_level = [isinstance(sub_item, (int, str)) for sub_item in item]

            if not all(is_scalar_level):
                levels_to_collapse = _get_axis_labels_to_collapse(indexer=item, axis_labels=self.axis_labels)

                subset_values_pandas_object = subset_values_pandas_object.droplevel(axis=1, level=levels_to_collapse)
                subset_mask_pandas_object = subset_mask_pandas_object.droplevel(axis=1, level=levels_to_collapse)

        # Compute the coordinate and axis labels.
        if isinstance(subset_values_pandas_object, pd.DataFrame):
            coordinate_labels, axis_labels = _compute_coordinate_and_axis_labels_for_pandas_index(
                subset_values_pandas_object.columns
            )
        else:
            coordinate_labels, axis_labels = (), ()

        # Compute the new cell shape to use to reshape the two-dimensional `pandas` object `values` to adhere to the
        # `coordinate_labels`.
        cell_shape = _compute_cell_shape(coordinate_labels)

        return TimeArray(
            sample_period=self.sample_period,
            start_time=self.start_time,
            end_time=self.end_time,
            as_of_time=self.as_of_time,
            values=subset_values_pandas_object.values.reshape(-1, *cell_shape),
            mask=subset_mask_pandas_object.values.astype(np.int8).reshape(-1, *cell_shape),
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
        )

    @classmethod
    def from_numpy_masked_array(
        cls,
        numpy_masked_array: np.ma.MaskedArray,
        sample_period: TimeDelta,
        start_time: Time,
        end_time: Time,
        as_of_time: Time,
        coordinate_labels: Optional[CoordinateLabels] = None,
        axis_labels: Optional[AxisLabels] = None,
    ) -> "TimeArray":
        """Constructs a time array from a `numpy.ma.MaskedArray` instance.

        Args:
            numpy_masked_array: numpy masked array
            sample_period: sample period
            start_time: start time
            end_time: end time
            as_of_time: as of time
            coordinate_labels: labels for individual coordinates
            axis_labels: names for individual axes

        Returns:
            time array
        """
        return TimeArray(
            sample_period=sample_period,
            start_time=start_time,
            end_time=end_time,
            as_of_time=as_of_time,
            values=numpy_masked_array.data,
            mask=np.array(numpy_masked_array.mask, dtype=int) if numpy_masked_array.mask is not False else None,
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
        )

    @classmethod
    def from_pandas_data_frame(
        cls, pandas_data_frame: pd.DataFrame, as_of_time: Time, mask: Optional[np.ndarray] = None
    ) -> "TimeArray":
        """Constructs a time array from a `pandas.DataFrame` instance.

        In order to use this constructor, the `pandas.DataFrame` instance must be indexed by a `pandas.DatetimeIndex`
        with a specified frequency which is used to define the `sample_period` of the `TimeArray`.

        Additionally, the `columns` must be instantiated with a named `pandas.Index`, which is used to define the
        `axis_labels` and `coordinate_labels` of the `TimeArray`.

        Args:
            pandas_data_frame: pandas data frame
            as_of_time: as of time
            mask: binary array with mask

        Returns:
            time array

        Raises:
            ValueError: if data frame does not represent a valid time array
        """
        sample_period, start_time, end_time = _process_pandas_object(pandas_object=pandas_data_frame)

        # Extract the coordinate and axis labels from the columns of the `pandas.DataFrame`.
        coordinate_labels, axis_labels = _compute_coordinate_and_axis_labels_for_pandas_index(
            pandas_index=pandas_data_frame.columns
        )

        # Ensure that the coordinate labels are integers or strings.
        for labels in coordinate_labels:
            for label in labels:
                if not isinstance(label, (int, str)):
                    raise ValueError("All coordinate labels must be integers or strings.")

        # Ensure that the axis labels are integers or strings.
        for axis_label in axis_labels:
            if not isinstance(axis_label, (int, str)):
                raise ValueError(
                    "Data frame columns must be instantiated with a named index to use as `axis_labels`. Names must "
                    "be integers or strings."
                )

        # Compute the cell shape given the coordinate labels.
        cell_shape = _compute_cell_shape(coordinate_labels=coordinate_labels)

        # Since `pandas.DataFrame.values` only holds two-dimensional data, reshape the data to adhere to the
        # `coordinate_labels`.
        values = pandas_data_frame.values.reshape(-1, *cell_shape)

        return TimeArray(
            sample_period=sample_period,
            start_time=start_time,
            end_time=end_time,
            as_of_time=as_of_time,
            values=values,
            mask=mask,
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
        )

    @classmethod
    def from_pandas_series(
        cls, pandas_series: pd.Series, as_of_time: Time, mask: Optional[np.ndarray] = None
    ) -> "TimeArray":
        """Constructs a time array from a `pandas.Series` instance.

        In order to use this constructor, the `pandas.Series` instance must be indexed by a `pandas.DatetimeIndex` with
        a specified frequency which is used to define the `sample_period` of the `TimeArray`.

        Additionally, the series must be named with an integer or string, which is used to define the
        `coordinate_labels` of the `TimeArray`.

        Args:
            pandas_series: pandas series
            as_of_time: as of time
            mask: binary array with mask

        Returns:
            time array
        """
        sample_period, start_time, end_time = _process_pandas_object(pandas_object=pandas_series)

        return TimeArray(
            sample_period=sample_period,
            start_time=start_time,
            end_time=end_time,
            as_of_time=as_of_time,
            values=pandas_series.values,
            mask=mask,
        )

    @classmethod
    def from_pandas_object(
        cls, pandas_object: Union[pd.Series, pd.DataFrame], as_of_time: Time, mask: Optional[np.ndarray] = None
    ) -> "TimeArray":
        """Constructs a time array from a `pandas.Series` or `pandas.DataFrame` instance.

        In order to use this constructor, the pandas object must be indexed by a `pandas.DatetimeIndex` with
        a specified frequency which is used to define the `sample_period` of the `TimeArray`.

        Additionally, if the object is a series, it must be named with an integer or string, which is used to define the
        `coordinate_labels` of the `TimeArray`. If the object is a data frame, the `columns` must be instantiated with
        a named `pandas.Index`, which is used to define the `axis_labels` and `coordinate_labels` of the `TimeArray`.

        Args:
            pandas_object: a pandas series or data frame
            as_of_time: as of time
            mask: binary array with mask

        Returns:
            time array

        Raises:
            ValueError: if object is neither a `pandas.Series` or `pandas.DataFrame`
        """
        if isinstance(pandas_object, pd.Series):
            time_array = cls.from_pandas_series(pandas_series=pandas_object, as_of_time=as_of_time, mask=mask)
        elif isinstance(pandas_object, pd.DataFrame):
            time_array = cls.from_pandas_data_frame(pandas_data_frame=pandas_object, as_of_time=as_of_time, mask=mask)
        else:
            raise ValueError("Object must be a `pandas.Series` or `pandas.DataFrame`.")

        return time_array

    def to_numpy_masked_array(self) -> np.ma.MaskedArray:
        """Returns the `numpy.ma.MaskedArray` equivalent of this time array."""
        return np.ma.masked_array(self.values, mask=self.mask)

    def to_pandas_data_frame(self, apply_mask: Optional[bool] = True) -> pd.DataFrame:
        """Returns the `pandas.DataFrame` equivalent of the values in this time array.

        Note that the `mask` of this time array will need to be extracted separately, as this method does not preserve
        the mask data.

        Args:
            apply_mask: whether or not to apply the internal `mask` before creating the data frame

        Returns:
            data frame

        Raises:
            ValueError: if the cells are dimensionless
        """
        if self.cell_shape == ():
            raise ValueError("Cells need to have one or more dimensions.")

        # Construct the values, optionally applying the internal `mask`.
        values = self.values.copy()
        if apply_mask and self.mask is not None:
            values[self.mask.astype(bool)] = np.nan

        index = pd.date_range(
            start=self.start_time.to_pandas_timestamp(),
            end=self.end_time.to_pandas_timestamp(),
            freq=self.sample_period.to_pandas_frequency(),
            name=_TIME_INDEX_NAME,
            closed="left",
        )

        return pd.DataFrame(
            index=index,
            columns=pd.MultiIndex.from_product(self.coordinate_labels, names=self.axis_labels),
            data=values.reshape(len(values), -1),
        )

    def to_pandas_series(self, apply_mask: Optional[bool] = True) -> pd.Series:
        """The `pandas.Series` equivalent of the `values` in this time array.

        Note that the `mask` of this time array will need to be extracted separately, as this method does not preserve
        the mask data.

        Args:
            apply_mask: whether or not to apply the internal `mask` before creating the series

        Returns:
            pandas series

        Raises:
            ValueError: if the cells are not dimensionless
        """
        if self.cell_shape != ():
            raise ValueError("Cells need to be dimensionless.")

        # Construct the values, optionally applying the internal `mask`.
        values = self.values.copy()
        if apply_mask and self.mask is not None:
            values[self.mask.astype(bool)] = np.nan

        index = pd.date_range(
            start=self.start_time.to_pandas_timestamp(),
            end=self.end_time.to_pandas_timestamp(),
            freq=self.sample_period.to_pandas_frequency(),
            name=_TIME_INDEX_NAME,
            closed="left",
        )

        return pd.Series(index=index, data=values)

    def to_pandas_object(self, apply_mask: Optional[bool] = True) -> Union[pd.Series, pd.DataFrame]:
        """The `pandas.Series` or `pandas.DataFrame` equivalent of the `values` in this time array.

        Note that the `mask` of this time array will need to be extracted separately.

        Args:
            apply_mask: whether or not to apply the internal `mask` before creating the pandas object

        Returns:
            pandas object (series or dataframe)
        """
        if len(self.cell_shape) == 0:
            return self.to_pandas_series(apply_mask=apply_mask)
        else:
            return self.to_pandas_data_frame(apply_mask=apply_mask)
