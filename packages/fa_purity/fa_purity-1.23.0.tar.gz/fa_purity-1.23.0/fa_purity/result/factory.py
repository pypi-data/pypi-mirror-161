from .core import (
    Result,
    ResultE,
)
from fa_purity.frozen import (
    FrozenDict,
)
from typing import (
    TypeVar,
)

_K = TypeVar("_K")
_V = TypeVar("_V")


def try_get(data: FrozenDict[_K, _V], key: _K) -> ResultE[_V]:
    if key in data:
        return Result.success(data[key])
    return Result.failure(KeyError(key))
