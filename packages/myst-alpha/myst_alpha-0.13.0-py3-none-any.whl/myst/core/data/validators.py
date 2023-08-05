from typing import Any, Optional

import numpy as np

from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta


def _num_periods_in_range(start_time: Time, end_time: Time, sample_period: TimeDelta) -> int:
    """Returns the number of periods in the given time range."""
    tdelta = end_time.to_pandas_timestamp() - start_time.to_pandas_timestamp()
    num_periods = tdelta / sample_period.to_pandas_frequency()
    if not num_periods.is_integer():
        raise ValueError("Period does not evenly divide time range.")

    return int(num_periods)


def check_arrays_same_length_as_time_range(
    start_time: Time, end_time: Time, sample_period: TimeDelta, values: np.ndarray, mask: Optional[np.ndarray]
) -> None:
    """Checks that values and mask arrays have the same length as the given time range."""
    num_periods = _num_periods_in_range(start_time=start_time, end_time=end_time, sample_period=sample_period)

    if len(values) != num_periods:
        raise ValueError("Values must have same length as time interval.")

    if mask is not None and len(mask) != num_periods:
        raise ValueError("Mask must have same length as time interval.")


def ensure_not_none(value: Any) -> Any:
    """Raises a ValueError if the given value is None."""
    if value is None:
        raise ValueError("Value cannot be `None`.")

    return value


def to_numpy_float_array(value: Any) -> np.ndarray:
    """Coerces the argument into a float-valued `np.ndarray` and returns it."""
    if not isinstance(value, np.ndarray) or value.dtype != float:
        return np.array(value, dtype=float)

    return value


def maybe_to_boolean_int_array(value: Any) -> Optional[np.ndarray]:
    """Checks that passed value contains only booleans or integers representing booleans and returns it."""
    if value is not None:
        if not isinstance(value, np.ndarray):
            value = np.array(value)

        if value.dtype not in (np.int8, int, bool) or not np.array_equal(value, value.astype(bool)):
            raise ValueError("Value must contain only boolean or boolean integer values.")

        return value.astype(np.int8)

    return value
