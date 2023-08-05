from typing import List, Optional

from myst.models import base_model
from myst.openapi.models.validation_error import ValidationError


class HTTPValidationError(base_model.BaseModel):
    """"""

    detail: Optional[List[ValidationError]] = None
