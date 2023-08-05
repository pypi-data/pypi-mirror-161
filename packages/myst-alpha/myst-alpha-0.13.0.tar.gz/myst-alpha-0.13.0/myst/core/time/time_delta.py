import datetime
import math
import re
from typing import Any, Generator, Optional, Tuple, Union

import pandas as pd
from pandas.tseries import offsets

PandasFrequency = Union[offsets.Day, offsets.Hour, offsets.Minute, offsets.Second]

_PANDAS_FREQUENCY_MAPPING = {
    offsets.Day: "days",
    offsets.Hour: "hours",
    offsets.Minute: "minutes",
    offsets.Second: "seconds",
}


# Define a regular expression to parse time delta ISO strings.
ISO_8601_PERIOD_REGEX = re.compile(
    r"^(?P<sign>[+-])?"
    r"P(?!\b)"
    r"(?P<years>[0-9]+([,.][0-9]+)?Y)?"
    r"(?P<months>[0-9]+([,.][0-9]+)?M)?"
    r"(?P<weeks>[0-9]+([,.][0-9]+)?W)?"
    r"(?P<days>[0-9]+([,.][0-9]+)?D)?"
    r"((?P<separator>T)(?P<hours>[0-9]+([,.][0-9]+)?H)?"
    r"(?P<minutes>[0-9]+([,.][0-9]+)?M)?"
    r"(?P<seconds>[0-9]+([,.][0-9]+)?S)?)?$"
)


def _parse_time_delta_string(iso_string: str) -> pd.DateOffset:
    regex_match = ISO_8601_PERIOD_REGEX.match(iso_string)

    if not regex_match:
        raise ValueError(f"Unable to parse ISO string `{iso_string}`.")

    regex_matched_groups = regex_match.groupdict()

    # Instantiate the `time_delta_dict`.
    time_delta_dict = dict()
    for time_delta_key, value in regex_matched_groups.items():
        if time_delta_key not in ("separator", "sign") and value is not None:

            # Parse the string time delta values.
            string_value = regex_matched_groups[time_delta_key][:-1].replace(",", ".")

            try:
                parsed_value = int(string_value)
            except ValueError:
                parsed_value = float(string_value)  # type: ignore

            if int(parsed_value) != parsed_value:
                raise ValueError(f"Passed value for `{time_delta_key}` must be an integer.")

            time_delta_dict[time_delta_key] = int(parsed_value)

    # If there is a negative sign at the beginning of the string, multiplier should be negative.
    if regex_matched_groups["sign"] == "-":
        time_delta_dict.update((key, value * -1) for key, value in time_delta_dict.items())

    return pd.DateOffset(**time_delta_dict)


def _format_time_delta(time_delta: pd.DateOffset) -> str:
    def update_sign(current_value: Union[int, float], current_sign: Optional[bool]) -> bool:
        if current_sign is None:
            if current_value >= 0:
                current_sign = True
            else:
                current_sign = False
        elif current_sign != (current_value >= 0):
            raise ValueError("Time delta cannot contain attributes that have mixed signs.")

        return current_sign

    # Set the default sign to undefined.
    sign = None

    # Format the date components of the time delta.
    formatted_time_delta = "P"
    for attribute, symbol in [("years", "Y"), ("months", "M"), ("weeks", "W"), ("days", "D")]:
        value = getattr(time_delta, attribute, None)

        if value is not None:
            if not isinstance(value, int):
                raise ValueError(f"Time delta `{attribute}` attribute must be an integer.")

            sign = update_sign(current_value=value, current_sign=sign)

            formatted_time_delta += f"{abs(value)}{symbol}"

    # Format the time components of the time delta.
    formatted_time_components = "T"
    for attribute, symbol in [("hours", "H"), ("minutes", "M")]:
        value = getattr(time_delta, attribute, None)

        if value is not None:
            sign = update_sign(current_value=value, current_sign=sign)

            formatted_time_components += f"{abs(value)}{symbol}"

    seconds = 0
    precision = 0
    for attribute, factor in [("seconds", 1), ("microseconds", 1e-6), ("nanoseconds", 1e-9)]:
        value = getattr(time_delta, attribute, None)

        if value is not None and value != 0:
            sign = update_sign(current_value=value, current_sign=sign)

            seconds += value * factor
            precision = abs(int(math.log10(factor)))

    if seconds != 0:
        formatted_time_components += f"{abs(seconds):.{precision}f}S"

    # Combine the components into the final formatted time delta.
    if len(formatted_time_components) > 1:
        formatted_time_delta += formatted_time_components

    # If needed, add the sign prefix to the formatted time delta.
    if not sign:
        formatted_time_delta = f"-{formatted_time_delta}"

    return formatted_time_delta


def _validate_time_delta(time_delta: pd.DateOffset) -> None:
    if not isinstance(time_delta, pd.DateOffset):
        raise TypeError("Time delta must be of type `pandas.DateOffset`.")

    for disallowed_attribute in [
        "year",
        "month",
        "day",
        "weekday",
        "hour",
        "minute",
        "second",
        "microsecond",
        "microseconds",
        "nanosecond",
        "nanoseconds",
    ]:
        if hasattr(time_delta, disallowed_attribute):
            raise ValueError(f"Time delta may not have `{disallowed_attribute}` attribute.")

    for allowed_attribute in ["years", "months", "weeks", "days", "hours", "minutes", "seconds"]:
        if hasattr(time_delta, allowed_attribute) and not isinstance(getattr(time_delta, allowed_attribute), int):
            raise ValueError(f"Time delta `{allowed_attribute}` attribute must be an integer.")


def _extract_pandas_date_offset_and_seconds(time_delta: "TimeDelta") -> Tuple[pd.DateOffset, float]:
    time_delta_pandas_date_offset = time_delta.to_pandas_date_offset()

    pandas_date_offset_kwargs = {}
    for attribute in ["years", "months", "weeks", "days"]:
        value = getattr(time_delta_pandas_date_offset, attribute, None)

        if value is not None and value != 0:
            pandas_date_offset_kwargs.update({attribute: value})

    pandas_date_offset = pd.DateOffset(**pandas_date_offset_kwargs)

    seconds = 0
    for attribute, factor in [("hours", 3600), ("minutes", 60), ("seconds", 1)]:
        value = getattr(time_delta_pandas_date_offset, attribute, None)

        if value is not None and value != 0:
            seconds += value * factor

    return pandas_date_offset, seconds


class TimeDelta:
    """Container for time delta objects that can be mapped from and to various third-party time objects.

    Note that `TimeDelta` respects calendar arithmetic for days, weeks, months, and years. This may cause mappings to
    some third-party time delta objects to fail, if they don't support this paradigm (e.g. `datetime.timedelta`).
    """

    def __init__(self, value: Union["TimeDelta", pd.DateOffset, PandasFrequency, datetime.timedelta, str]) -> None:
        """A `TimeDelta` container is initialized with a date offset, time delta, or ISO 8601 formatted string.

        The full ISO 8601 format specification is `PnYnMnDTnHnMnS`.

        Note that we only support integer values for all `n` and thus do not have support for sub-second precision.

        Args:
            value: date offset, time delta, or ISO 8601 formatted string
        """
        self._time_delta: pd.DateOffset

        if isinstance(value, TimeDelta):
            self._time_delta = value._time_delta
        elif isinstance(value, (offsets.Day, offsets.Hour, offsets.Minute, offsets.Second)):
            attribute = _PANDAS_FREQUENCY_MAPPING[type(value)]
            self._time_delta = pd.DateOffset(**{attribute: value.n})
        elif isinstance(value, pd.DateOffset):
            _validate_time_delta(value)
            self._time_delta = value
        elif isinstance(value, datetime.timedelta):
            if not value.total_seconds().is_integer():
                raise ValueError("Sub-second precision is not supported.")
            self._time_delta = pd.DateOffset(hours=value.days * 24, seconds=value.seconds)
        elif isinstance(value, str):
            self._time_delta = _parse_time_delta_string(value)
        else:
            raise TypeError(
                "Argument to `TimeDelta` constructor must be of type `TimeDelta`, `pd.DateOffset`, "
                "`datetime.timedelta`, or `str`."
            )

    def __eq__(self, other: object) -> bool:
        """Returns True if this time delta and `other` represent the same time delta, False otherwise."""
        return isinstance(other, TimeDelta) and _extract_pandas_date_offset_and_seconds(
            time_delta=self
        ) == _extract_pandas_date_offset_and_seconds(time_delta=other)

    def __ne__(self, other: object) -> bool:
        """Returns False if this time delta and `other` represent the same time delta, True otherwise."""
        return not self.__eq__(other)

    def __repr__(self) -> str:
        """Returns an encapsulated ISO 8601 formatted string representation for this time delta."""
        return f"<TimeDelta: {self.to_iso_string()}>"

    def __str__(self) -> str:
        """Returns the ISO 8601 formatted string representation for this time."""
        return self.to_iso_string()

    def to_iso_string(self) -> str:
        """Returns the ISO 8601 formatted string representation of this time."""
        return _format_time_delta(self._time_delta)

    def to_pandas_date_offset(self) -> pd.DateOffset:
        """Returns the `pandas.DateOffset` equivalent of this time delta."""
        return self._time_delta

    def to_pandas_frequency(self) -> pd.DateOffset:
        """Returns the pandas frequency equivalent of this time delta."""
        for attribute in ["years", "months", "weeks"]:
            if hasattr(self._time_delta, attribute):
                raise ValueError(f"Cannot convert `{attribute}` attribute, because calendar arithmetic is ambiguous.")

        pandas_frequency = None
        for attribute, pandas_date_offset_type in [
            ("days", offsets.Day),
            ("hours", offsets.Hour),
            ("minutes", offsets.Minute),
            ("seconds", offsets.Second),
        ]:
            value = getattr(self._time_delta, attribute, None)

            if value is not None:
                if pandas_frequency is not None:
                    raise ValueError("Cannot convert to frequency if multiple attributes are specified.")
                if value <= 0:
                    raise ValueError("Frequency must be positive.")

                pandas_frequency = pandas_date_offset_type(value)

        return pandas_frequency

    def to_pandas_timedelta(self) -> pd.Timedelta:
        """Returns the `pandas.Timedelta` equivalent of this time delta."""
        for attribute in ["years", "months", "weeks", "days"]:
            if hasattr(self._time_delta, attribute):
                raise ValueError(
                    f"Cannot convert `{attribute}` attribute, because calendar arithmetic is not supported."
                )

        pandas_timedelta_kwargs = {}
        for attribute in ["hours", "minutes", "seconds", "microseconds", "nanoseconds"]:
            value = getattr(self._time_delta, attribute, None)

            if value is not None:
                pandas_timedelta_kwargs[attribute] = value

        return pd.Timedelta(**pandas_timedelta_kwargs)

    def to_datetime_timedelta(self) -> datetime.timedelta:
        """Returns the `datetime.timedelta` equivalent of this time delta."""
        return self.to_pandas_timedelta().to_pytimedelta()

    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> "TimeDelta":
        return cls(v)
