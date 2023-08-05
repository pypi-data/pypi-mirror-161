from __future__ import (
    annotations,
)

from decimal import (
    Decimal,
)
from typing import (
    Type,
    TypeVar,
    Union,
)
from typing_extensions import (
    TypeGuard,
)

_T = TypeVar("_T")
Primitive = Union[str, int, float, Decimal, bool, None]
PrimitiveTypes = Union[
    Type[str],
    Type[int],
    Type[float],
    Type[Decimal],
    Type[bool],
    Type[None],
]
PrimitiveTypesList = (
    str,
    int,
    float,
    Decimal,
    bool,
    type(None),
)
PrimitiveTVar = TypeVar(  # Deprecated use NotNonePrimTvar instead
    "PrimitiveTVar", str, int, float, Decimal, bool, Type[None]
)
NotNonePrimTvar = TypeVar("NotNonePrimTvar", str, int, float, Decimal, bool)


def is_primitive(raw: _T) -> TypeGuard[Primitive]:
    if raw is None or isinstance(raw, PrimitiveTypesList):
        return True
    return False
