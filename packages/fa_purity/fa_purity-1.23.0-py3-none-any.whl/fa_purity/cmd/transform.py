from fa_purity.cmd.core import (
    Cmd,
    unsafe_unwrap,
)
from fa_purity.frozen import (
    FrozenList,
)
from typing import (
    Callable,
    TypeVar,
)

_T = TypeVar("_T")
_R = TypeVar("_R")


Mapper = Callable[[Callable[[_T], _R], FrozenList[_T]], FrozenList[_R]]


def merge(
    mapper: Mapper[Cmd[_T], _T], items: FrozenList[Cmd[_T]]
) -> Cmd[FrozenList[_T]]:
    def _action() -> FrozenList[_T]:
        return mapper(lambda i: unsafe_unwrap(i), items)

    return Cmd.from_cmd(_action)


def serial_merge(items: FrozenList[Cmd[_T]]) -> Cmd[FrozenList[_T]]:
    return merge(lambda f, i: tuple(map(f, i)), items)
