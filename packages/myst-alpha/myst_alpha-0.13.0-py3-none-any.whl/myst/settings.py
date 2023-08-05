import pathlib
from typing import Optional

import pydantic

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()


class Settings(pydantic.BaseSettings):
    """Runtime settings for the Myst client."""

    MYST_API_HOST: str = "https://api.myst.ai"

    # Increase default timeout, since it's insufficient for some longer inserts/retrievals.
    API_TIMEOUT_SEC: int = 30

    MYST_APPLICATION_CREDENTIALS: Optional[pathlib.Path] = None

    @pydantic.validator("MYST_APPLICATION_CREDENTIALS")
    def validate_service_account_key_path(cls, v: Optional[str]) -> Optional[pathlib.Path]:
        """Makes sure the service account key is a valid path."""
        if isinstance(v, pathlib.Path):
            return v
        elif isinstance(v, str):
            return pathlib.Path(v)
        elif v is None:
            return None
        else:
            raise ValueError("`MYST_APPLICATION_CREDENTIALS` must be a string if set.")


settings = Settings()
