from functools import singledispatch
from typing import Any, List, Mapping, Optional, Tuple, TypeVar, Union
from uuid import UUID


class Unset:
    pass


UNSET = Unset()
UUIDOrStr = Union[str, UUID]
IntOrStr = Union[int, str]
Shape = Tuple[int, ...]
CoordinateLabels = Tuple[Tuple[IntOrStr, ...], ...]
AxisLabels = Tuple[IntOrStr, ...]
Metadata = Mapping[str, Union[str, int, float, bool, None]]

# Note: This should be a recursive type alias but `mypy` doesn't support that, so use `List[Any]` instead to allow for
#   an arbitrary amount of nesting.
ItemOrSlice = Union[Tuple[Union[IntOrStr, List[Any]], ...], List[Any], IntOrStr]

T = TypeVar("T")
OptionalArgument = Union[Optional[T], Unset]


@singledispatch
def to_uuid(uuid: UUIDOrStr) -> UUID:
    raise NotImplementedError()


@to_uuid.register
def _uuid_to_uuid(uuid: UUID) -> UUID:
    return uuid


@to_uuid.register
def _str_to_uuid(uuid: str) -> UUID:
    return UUID(uuid)
