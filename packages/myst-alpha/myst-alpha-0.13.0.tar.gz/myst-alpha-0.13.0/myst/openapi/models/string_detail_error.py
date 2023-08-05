from myst.models import base_model


class StringDetailError(base_model.BaseModel):
    """Pydantic model used to describe a simple string detail error."""

    detail: str
