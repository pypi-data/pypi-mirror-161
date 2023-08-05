from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity._patch import (
    Patch,
)
import sys
from typing import (
    Callable,
    Generic,
    NoReturn,
    TypeVar,
)

_A = TypeVar("_A")
_B = TypeVar("_B")


@dataclass(frozen=True)
class Cmd(Generic[_A]):
    # Equivalent to haskell IO type
    # unsafe_unwrap not included as method for discouraging its use
    _value: Patch[Callable[[], _A]]

    @staticmethod
    def from_cmd(value: Callable[[], _A]) -> Cmd[_A]:
        return Cmd(Patch(value))

    def map(self, function: Callable[[_A], _B]) -> Cmd[_B]:
        return Cmd(Patch(lambda: function(self._value.unwrap())))

    def bind(self, function: Callable[[_A], Cmd[_B]]) -> Cmd[_B]:
        return Cmd(
            Patch(lambda: function(self._value.unwrap())._value.unwrap())
        )

    def apply(self, wrapped: Cmd[Callable[[_A], _B]]) -> Cmd[_B]:
        return wrapped.bind(lambda f: self.map(f))

    def compute(self) -> NoReturn:
        self._value.unwrap()
        sys.exit(0)

    def __add__(self, other: Cmd[_B]) -> Cmd[_B]:
        return self.bind(lambda _: other)


@dataclass(frozen=True)
class _CmdUnwrapper:
    pass


@dataclass(frozen=True)
class CmdUnwrapper:
    # Do not build any public constructors or instances
    # This obj is only accessible in the action context through the `new_cmd` builder
    _inner: _CmdUnwrapper

    @staticmethod
    def unwrap(action: Cmd[_A]) -> _A:
        return action._value.unwrap()


_unwrapper = CmdUnwrapper(_CmdUnwrapper())


def new_cmd(action: Callable[[CmdUnwrapper], _A]) -> Cmd[_A]:
    return Cmd(Patch(lambda: action(_unwrapper)))


def unsafe_unwrap(action: Cmd[_A]) -> _A:
    # This is an unsafe constructor (type-check cannot ensure its proper use)
    # Do not use until is strictly necessary
    # WARNING: this is equivalent to compute, and will execute the Cmd
    #
    # Only use when all actions (Cmd[_A]) result in the same output instance (_A)
    # and side effects are not present or negligible.
    # e.g. unwrap a cmd when used on a cached function definition
    #
    # [NOTICE] Do not use this function for defining a new Cmd, use `new_cmd` instead
    return action._value.unwrap()
