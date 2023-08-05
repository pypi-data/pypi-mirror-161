from datetime import datetime
from typing import Any, Generator, Union

import pandas as pd

from myst.core.time.time_delta import TimeDelta


class Time:
    """Container for time zone-aware time objects that can be mapped from and to various third-party time objects."""

    def __init__(self, value: Union["Time", datetime, str]) -> None:
        """A `Time` container is initialized with a datetime or an ISO 8601 formatted string.

        The full ISO 8601 format specification is `YYYY-MM-DDThh:mm:ssZ`. The `Z` suffix indicates the UTC time zone.

        Note that we only support ISO strings that are in UTC, to avoid possible ambiguity around daylight savings.

        Args:
            value: ISO 8601 formatted string in UTC, or time zone-aware datetime
        """
        self._time: pd.Timestamp

        if isinstance(value, Time):
            self._time = value._time
        elif isinstance(value, datetime):
            pandas_timestamp = pd.Timestamp(value)

            if pandas_timestamp.tz is None:
                raise ValueError("Input timestamp must be time zone-aware.")

            self._time = pandas_timestamp.tz_convert(tz="UTC")
        elif isinstance(value, str):
            if not value.endswith("Z"):
                raise ValueError("The UTC time zone in passed ISO string must be indicated by the `Z` suffix.")

            pandas_timestamp = pd.Timestamp(value)

            if pandas_timestamp.tz.zone != "UTC":
                raise ValueError("The time zone in passed ISO string must be UTC, because it is ambiguous otherwise.")

            self._time = pandas_timestamp
        else:
            raise TypeError("Argument to `Time` constructor must be `Time`, datetime, or str.")

    def __eq__(self, other: object) -> bool:
        """Returns True if this time and other represent the same instant in time, False otherwise."""
        return isinstance(other, Time) and self._time == other._time

    def __ne__(self, other: object) -> bool:
        """Returns True if this time and other do not represent the same instant in time, False otherwise."""
        return not self.__eq__(other)

    def __add__(self, other: TimeDelta) -> "Time":
        """Returns a new `Time` resulting from the addition of this object and the provided `TimeDelta`."""
        if not isinstance(other, TimeDelta):
            raise ValueError("Only a `TimeDelta` instance may be added to a `Time`.")

        return Time(pd.Timestamp(self.to_pandas_timestamp() + other.to_pandas_date_offset()))

    def __radd__(self, other: Any) -> "Time":
        """Returns a new `Time` resulting from the addition of this object and the provided `TimeDelta`."""
        return self.__add__(other)

    def __sub__(self, other: TimeDelta) -> "Time":
        """Returns a new `Time` resulting from the subtraction of the provided `TimeDelta` from this object."""
        if not isinstance(other, TimeDelta):
            raise ValueError("Only a `TimeDelta` instance may be subtracted from a `Time`.")

        return Time(pd.Timestamp(self.to_pandas_timestamp() - other.to_pandas_date_offset()))

    def __lt__(self, other: "Time") -> bool:
        """Returns True if this time is less than the passed time, False otherwise."""
        return self._time < other._time

    def __le__(self, other: "Time") -> bool:
        """Returns True if this time is less than or equal to the passed time, False otherwise."""
        return self._time <= other._time

    def __gt__(self, other: "Time") -> bool:
        """Returns True if this time is greater than the passed time, False otherwise."""
        return self._time > other._time

    def __ge__(self, other: "Time") -> bool:
        """Returns True if this time is greater than or equal to the passed time, False otherwise."""
        return self._time >= other._time

    def __repr__(self) -> str:
        """Returns an encapsulated ISO 8601 formatted string representation for this time."""
        return f"<Time: {self.to_iso_string()}>"

    def __str__(self) -> str:
        """Returns the ISO 8601 formatted string representation for this time."""
        return self.to_iso_string()

    def __hash__(self) -> int:
        """Returns a hash value for this time."""
        return hash(self._time)

    def to_iso_string(self) -> str:
        """Returns the ISO 8601 formatted string representation of this time."""
        return self._time.isoformat().replace("+00:00", "Z")

    def to_pandas_timestamp(self) -> pd.Timestamp:
        """Returns the `pandas.Timestamp` equivalent of this time."""
        return self._time

    def to_datetime(self) -> datetime:
        """Returns the `datetime.datetime` equivalent of this time."""
        return self._time.to_pydatetime()

    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> "Time":
        return cls(v)
