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
class InnerPureIter(
    Generic[_T],
):
    # In this case Cmd models mutation not side effects
    # all produced iterables are supposed to be semanticly equivalent
    new_iter: Cmd[Iterable[_T]]
