from typing import Optional, Union

import pydantic

from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.base_model import BaseModel
from myst.models.types import OptionalArgument, Unset


class Timing(BaseModel):
    class Config:
        extra = pydantic.Extra.ignore


class AbsoluteTiming(Timing):
    time: Time


class RelativeTiming(Timing):
    frequency: Optional[TimeDelta] = None
    offset: Optional[TimeDelta] = None
    time_zone: Optional[str] = "UTC"


class CronTiming(Timing):
    cron_expression: str
    time_zone: Optional[str] = "UTC"


ScheduleTiming = Union[AbsoluteTiming, CronTiming, RelativeTiming]
AbsoluteOrRelativeTiming = Union[AbsoluteTiming, RelativeTiming]
AbsoluteOrCronTiming = Union[AbsoluteTiming, CronTiming]
TimeRangeBoundary = Union[Time, TimeDelta, AbsoluteOrRelativeTiming]


def from_time_range_boundary(
    timing: OptionalArgument[Union[Time, TimeDelta, AbsoluteOrRelativeTiming]]
) -> OptionalArgument[AbsoluteOrRelativeTiming]:
    """Returns the given argument as a timing appropriate for a time range boundary.

    If an `AbsoluteOrRelativeTiming`, `None` or `UNSET` is passed, it will be returned unchanged.

    If a `Time` is passed, it will be interpreted as specifying a fixed point in time, and an `AbsoluteTiming` will be
    returned.

    If a `TimeDelta` is passed, it will be interpreted as the "offset" of a `RelativeTiming`. The corresponding
    `RelativeTiming` will be returned.

    Args:
        timing: the input time specifier to be interpreted

    Returns:
        the timing, after interpretation

    Raises:
        TypeError: if the argument is of a type that cannot be understood as a time range boundary
    """
    if timing is None or isinstance(timing, (AbsoluteTiming, RelativeTiming)):
        return timing
    elif isinstance(timing, Unset):
        return timing
    elif isinstance(timing, Time):
        # Interpret as fixed point in time.
        return AbsoluteTiming(time=timing)
    elif isinstance(timing, TimeDelta):
        # Interpret as offset (notably, not frequency).
        return RelativeTiming(offset=timing)
    else:
        raise TypeError("Argument must be of type `Time`, `TimeDelta, `Timing`, or None.")


def from_schedule_specifier(
    timing: OptionalArgument[Union[Time, TimeDelta, ScheduleTiming]]
) -> OptionalArgument[Optional[ScheduleTiming]]:
    """Returns the given argument as a timing appropriate for scheduling.

    If a `None` is passed, `None` will be returned.

    If a `UNSET` is passed, `UNSET` will be returned.

    If a `Time` is passed, it will be interpreted as specifying a fixed point in time, and an `AbsoluteTiming` will
    be returned.

    If a `TimeDelta` is passed, it will be interpreted as the "frequency" of a `RelativeTiming`. The corresponding
    `RelativeTiming` will be returned.

    If a `ScheduleTiming` is passed, it will be returned unaltered.

    Args:
        timing: the input time specifier to be interpreted

    Returns:
        the timing, after interpretation

    Raises:
        TypeError: if the argument is of a type that cannot be understood as a schedule timing
    """
    if timing is None:
        return timing
    elif isinstance(timing, Unset):
        return timing
    elif isinstance(timing, Time):
        return AbsoluteTiming(time=timing)
    elif isinstance(timing, TimeDelta):
        return RelativeTiming(frequency=timing)
    elif isinstance(timing, (AbsoluteTiming, RelativeTiming, CronTiming)):
        return timing
    else:
        raise TypeError("Argument must be of type `Time`, `TimeDelta, or `ScheduleTiming`.")
