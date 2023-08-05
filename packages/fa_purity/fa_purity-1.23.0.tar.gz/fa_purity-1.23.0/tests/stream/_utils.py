from fa_purity.cmd import (
    Cmd,
    unsafe_unwrap,
)
from fa_purity.stream.core import (
    Stream,
)
from secrets import (
    randbelow,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")


def rand_int() -> Cmd[int]:
    return Cmd.from_cmd(lambda: randbelow(11))


def assert_different_iter(stm: Stream[_T]) -> None:
    iter1 = unsafe_unwrap(stm.unsafe_to_iter())
    iter2 = unsafe_unwrap(stm.unsafe_to_iter())
    assert id(iter1) != id(iter2)
