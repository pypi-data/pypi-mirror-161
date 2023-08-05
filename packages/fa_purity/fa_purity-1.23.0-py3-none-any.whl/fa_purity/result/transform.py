from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.result.core import (
    Result,
    UnwrapError,
)
from typing import (
    cast,
    TypeVar,
)

_S = TypeVar("_S")
_F = TypeVar("_F")


def all_ok(items: FrozenList[Result[_S, _F]]) -> Result[FrozenList[_S], _F]:
    try:
        return Result.success(tuple(i.unwrap() for i in items))
    except UnwrapError as err:
        _err = cast(UnwrapError[_S, _F], err)
        return Result.failure(_err.container.unwrap_fail())
