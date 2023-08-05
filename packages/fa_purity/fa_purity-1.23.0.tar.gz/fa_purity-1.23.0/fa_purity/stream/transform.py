from ._inner import (
    InnerStream,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    Cmd,
    unsafe_unwrap,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.core import (
    PureIter,
)
from fa_purity.stream.core import (
    Stream,
)
from fa_purity.stream.factory import (
    from_piter,
)
from typing import (
    Optional,
    TypeVar,
    Union,
)

_T = TypeVar("_T")


def _chain_1(
    unchained: Stream[PureIter[_T]],
) -> Stream[_T]:
    return unchained.map(
        lambda p: p.map(lambda x: Cmd.from_cmd(lambda: x)).transform(
            lambda x: from_piter(x)
        )
    ).bind(lambda x: x)


def _chain_2(
    unchained: PureIter[Stream[_T]],
) -> Stream[_T]:
    return (
        unchained.map(lambda s: Cmd.from_cmd(lambda: s))
        .transform(lambda x: from_piter(x))
        .bind(lambda x: x)
    )


def chain(
    unchained: Union[Stream[PureIter[_T]], PureIter[Stream[_T]]],
) -> Stream[_T]:
    if isinstance(unchained, Stream):
        return _chain_1(unchained)
    return _chain_2(unchained)


def squash(stm: Stream[Cmd[_T]]) -> Stream[_T]:
    items = InnerStream(stm.unsafe_to_iter().bind(_iter_factory.squash))
    return Stream(items)


def consume(stm: Stream[Cmd[None]]) -> Cmd[None]:
    return Cmd.from_cmd(
        lambda: _iter_factory.deque(
            iter(unsafe_unwrap(a) for a in unsafe_unwrap(stm.unsafe_to_iter()))
        )
    )


def filter_opt(stm: Stream[Optional[_T]]) -> Stream[_T]:
    items = InnerStream(stm.unsafe_to_iter().map(_iter_factory.filter_none))
    return Stream(items)


def filter_maybe(stm: Stream[Maybe[_T]]) -> Stream[_T]:
    return filter_opt(stm.map(lambda x: x.value_or(None)))


def until_none(stm: Stream[Optional[_T]]) -> Stream[_T]:
    items = InnerStream(stm.unsafe_to_iter().map(_iter_factory.until_none))
    return Stream(items)


def until_empty(stm: Stream[Maybe[_T]]) -> Stream[_T]:
    return until_none(stm.map(lambda m: m.value_or(None)))
