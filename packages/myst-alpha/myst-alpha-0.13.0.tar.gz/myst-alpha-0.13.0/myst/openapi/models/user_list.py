from typing import List

from myst.models import base_model
from myst.openapi.models.user_get import UserGet


class UserList(base_model.BaseModel):
    """Schema for user list responses."""

    data: List[UserGet]
    has_more: bool
