from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.cron_timing_create import CronTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


class BacktestCreate(base_model.BaseModel):
    """Schema for backtest create requests."""

    title: str
    test_start_time: str
    test_end_time: str
    fit_start_timing: Union[AbsoluteTimingCreate, RelativeTimingCreate]
    fit_end_timing: Union[AbsoluteTimingCreate, RelativeTimingCreate]
    fit_reference_timing: Union[AbsoluteTimingCreate, CronTimingCreate]
    predict_start_timing: RelativeTimingCreate
    predict_end_timing: RelativeTimingCreate
    predict_reference_timing: CronTimingCreate
    model: str
    object_: Optional[Literal["Backtest"]] = Field("Backtest", alias="object")
    description: Optional[str] = None
