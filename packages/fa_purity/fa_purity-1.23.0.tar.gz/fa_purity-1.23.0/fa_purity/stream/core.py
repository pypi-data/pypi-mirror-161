from __future__ import (
    annotations,
)

from ._inner import (
    InnerStream,
)
from dataclasses import (
    dataclass,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.maybe import (
    Maybe,
)
import functools
from typing import (
    Callable,
    Generic,
    Iterable,
    TypeVar,
)

_T = TypeVar("_T")
_R = TypeVar("_R")


@dataclass(frozen=True)
class Stream(Generic[_T]):
    # unsafe_unwrap use is safe due to iters equivalence
    _inner: InnerStream[_T]

    def map(self, function: Callable[[_T], _R]) -> Stream[_R]:
        items: Cmd[Iterable[_R]] = self._inner.new_iter.map(
            lambda i: iter(map(function, i))
        )
        return Stream(InnerStream(items))

    def reduce(self, function: Callable[[_R, _T], _R], init: _R) -> Cmd[_R]:
        return self._inner.new_iter.map(
            lambda i: functools.reduce(function, i, init)
        )

    def bind(self, function: Callable[[_T], Stream[_R]]) -> Stream[_R]:
        items = (
            self.map(function)
            .unsafe_to_iter()
            .map(lambda items: iter(i.unsafe_to_iter() for i in items))
            .bind(lambda x: _iter_factory.squash(x))
            .map(lambda x: _iter_factory.chain(x))
        )
        return Stream(InnerStream(items))

    def filter(self, function: Callable[[_T], bool]) -> Stream[_T]:
        items: Cmd[Iterable[_T]] = self._inner.new_iter.map(
            lambda i: iter(filter(function, i))
        )
        return Stream(InnerStream(items))

    def find_first(self, criteria: Callable[[_T], bool]) -> Cmd[Maybe[_T]]:
        return self._inner.new_iter.map(
            lambda i: _iter_factory.find_first(criteria, i)
        ).map(lambda x: Maybe.from_optional(x))

    def chunked(self, size: int) -> Stream[FrozenList[_T]]:
        items: Cmd[Iterable[FrozenList[_T]]] = self._inner.new_iter.map(
            lambda i: _iter_factory.chunked(i, size)
        )
        return Stream(InnerStream(items))

    def transform(self, function: Callable[[Stream[_T]], _R]) -> _R:
        return function(self)

    def to_list(self) -> Cmd[FrozenList[_T]]:
        return self._inner.new_iter.map(tuple)

    def unsafe_to_iter(self) -> Cmd[Iterable[_T]]:
        # if possible iterables should not be used directly
        return self._inner.new_iter
