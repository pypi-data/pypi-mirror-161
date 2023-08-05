import pydantic

from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta


class BaseModel(pydantic.BaseModel):
    """Base pydantic model to use throughout client library models.

    This model imbues all subclasses with the `json_encoders` specified in its `Config`. This means that types that
    normally wouldn't be serializable will be run through those encoders first.
    """

    class Config:
        json_encoders = {Time: Time.to_iso_string, TimeDelta: TimeDelta.to_iso_string}
