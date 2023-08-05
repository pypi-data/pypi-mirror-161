import pydantic


class BaseModel(pydantic.BaseModel):
    """Base model for all request and response models to inherit from."""

    # Modification encouraged!
    class Config:
        pass
