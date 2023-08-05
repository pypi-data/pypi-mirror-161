from dataclasses import (
    dataclass,
)
from fa_purity.cmd import (
    Cmd,
)
from typing import (
    Generic,
    Iterable,
    TypeVar,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class InnerStream(
    Generic[_T],
):
    new_iter: Cmd[Iterable[_T]]
