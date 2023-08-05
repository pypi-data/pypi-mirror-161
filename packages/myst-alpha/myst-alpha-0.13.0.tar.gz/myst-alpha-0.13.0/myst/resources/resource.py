from typing import Optional
from uuid import UUID

from myst.core.time.time import Time
from myst.models.base_model import BaseModel


class Resource(BaseModel):
    """Represents an API resource with a persistent identity.

    Attributes:
        uuid: the universally unique identifier for this resource
        create_time: the time when the resource was created
        update_time: the time when the resource was last modified
    """

    uuid: UUID
    create_time: Time
    update_time: Optional[Time] = None


class ShareableResource(Resource):
    """A resource associated with an owner, organization, and creator.

    Attributes:
        organization: the identifier of the organization this resource belongs to
        owner: the identifier of the user who owns this resource
        creator: the identifier of the user who created this resource
    """

    organization: UUID
    owner: UUID
    creator: UUID
