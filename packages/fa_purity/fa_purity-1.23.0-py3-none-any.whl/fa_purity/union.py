from dataclasses import (
    dataclass,
)
from deprecated import (
    deprecated,
)
from typing import (
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

_L = TypeVar("_L")
_R = TypeVar("_R")


@deprecated("use `UnionFactory` instead")  # type: ignore[misc]
def inr(val: _R, _left: Optional[Type[_L]] = None) -> Union[_L, _R]:
    return val


@deprecated("use `UnionFactory` instead")  # type: ignore[misc]
def inl(val: _L, _right: Optional[Type[_L]] = None) -> Union[_L, _R]:
    return val


@dataclass(frozen=True)
class UnionFactory(Generic[_L, _R]):
    def inl(self, value: _L) -> Union[_L, _R]:
        return value

    def inr(self, value: _R) -> Union[_L, _R]:
        return value
