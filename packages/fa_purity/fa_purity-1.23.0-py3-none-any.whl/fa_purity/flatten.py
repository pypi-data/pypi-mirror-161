from fa_purity.cmd import (
    Cmd,
)
from fa_purity.cmd.transform import (
    serial_merge,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.result import (
    Result,
)
from fa_purity.result.transform import (
    all_ok,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")
_S = TypeVar("_S")
_F = TypeVar("_F")


def flatten_cmds(items: FrozenList[Cmd[_T]]) -> Cmd[FrozenList[_T]]:
    """serial_merge function alias"""
    return serial_merge(items)


def flatten_results(
    items: FrozenList[Result[_S, _F]]
) -> Result[FrozenList[_S], _F]:
    """all_ok function alias"""
    return all_ok(items)
