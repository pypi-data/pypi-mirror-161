from typing import TYPE_CHECKING, Any, Dict, Union
from uuid import UUID

from myst.models.types import UNSET

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.models.types import UUIDOrStr
    from myst.resources.resource import Resource


def drop_unset_values(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Drops `UNSET` values from the specified dictionary.

    Args:
        input_dict: the dictionary to drop `UNSET` values from

    Returns:
        the resulting dictionary
    """
    output_dict = {key: value for key, value in input_dict.items() if value is not UNSET}

    return output_dict


def get_resource_uuid(resource: Union["Resource", "UUIDOrStr"]) -> UUID:
    """Extracts the UUID from the specified resource."""
    if isinstance(resource, UUID):
        return resource
    if isinstance(resource, str):
        return UUID(resource)
    else:
        return resource.uuid
