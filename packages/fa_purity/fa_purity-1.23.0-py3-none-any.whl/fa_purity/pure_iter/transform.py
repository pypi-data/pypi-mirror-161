from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.cmd.core import (
    CmdUnwrapper,
    new_cmd,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.core import (
    PureIter,
)
from fa_purity.pure_iter.factory import (
    unsafe_from_cmd,
)
from typing import (
    Optional,
    TypeVar,
)

_T = TypeVar("_T")


def chain(
    unchained: PureIter[PureIter[_T]],
) -> PureIter[_T]:
    return unchained.bind(lambda x: x)


def consume(p_iter: PureIter[Cmd[None]]) -> Cmd[None]:
    def _action(act: CmdUnwrapper) -> None:
        for c in p_iter:
            act.unwrap(c)

    return new_cmd(_action)


def filter_opt(items: PureIter[Optional[_T]]) -> PureIter[_T]:
    return unsafe_from_cmd(
        Cmd.from_cmd(lambda: _iter_factory.filter_none(items))
    )


def filter_maybe(items: PureIter[Maybe[_T]]) -> PureIter[_T]:
    return filter_opt(items.map(lambda x: x.value_or(None)))


def until_none(items: PureIter[Optional[_T]]) -> PureIter[_T]:
    return unsafe_from_cmd(
        Cmd.from_cmd(lambda: _iter_factory.until_none(items))
    )


def until_empty(items: PureIter[Maybe[_T]]) -> PureIter[_T]:
    return until_none(items.map(lambda m: m.value_or(None)))
