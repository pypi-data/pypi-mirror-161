from typing import Union

from myst.models.timing import AbsoluteTiming, CronTiming, RelativeTiming, Timing
from myst.models.types import UNSET, OptionalArgument
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.cron_timing_create import CronTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


def to_timing_create(
    timing: OptionalArgument[Timing],
) -> OptionalArgument[Union[AbsoluteTimingCreate, RelativeTimingCreate, CronTimingCreate]]:
    """Returns the appropriate OpenAPI model for the given timing, or None if timing is None."""
    if timing is None:
        return None
    elif timing is UNSET:
        return UNSET
    elif isinstance(timing, AbsoluteTiming):
        return AbsoluteTimingCreate(object="Timing", type="AbsoluteTiming", time=timing.time.to_iso_string())
    elif isinstance(timing, RelativeTiming):
        return RelativeTimingCreate(
            object="Timing",
            type="RelativeTiming",
            frequency=timing.frequency.to_iso_string() if timing.frequency else None,
            offset=timing.offset.to_iso_string() if timing.offset else None,
            time_zone=timing.time_zone,
        )
    elif isinstance(timing, CronTiming):
        return CronTimingCreate(
            object="Timing", type="CronTiming", cron_expression=timing.cron_expression, time_zone=timing.time_zone
        )
    else:
        raise TypeError("Argument `timing` must be of type `Timing` or None.")
