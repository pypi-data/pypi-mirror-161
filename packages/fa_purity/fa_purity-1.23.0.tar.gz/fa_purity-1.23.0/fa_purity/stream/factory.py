from ._inner import (
    InnerStream,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.pure_iter.core import (
    PureIter,
)
from fa_purity.stream.core import (
    Stream,
)
from typing import (
    Iterable,
    TypeVar,
)

_T = TypeVar("_T")


def unsafe_from_cmd(cmd: Cmd[Iterable[_T]]) -> Stream[_T]:
    # [WARNING] unsafe constructor
    # - Type-check cannot ensure its proper use
    # - Do not use until is strictly necessary
    # - Do unit test over the function defined by this
    #
    # As with `PureIter unsafe_from_cmd` the cmd must return a new iterable
    # object in each call to ensure that the stream is never consumed,
    # nevertheless they can be semanticly different iterables.
    return Stream(InnerStream(cmd))


def from_piter(piter: PureIter[Cmd[_T]]) -> Stream[_T]:
    items = InnerStream(_iter_factory.squash(piter))
    return Stream(items)
