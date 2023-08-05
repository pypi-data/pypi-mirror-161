from fa_purity.cmd import (
    Cmd,
)
from fa_purity.cmd.core import (
    CmdUnwrapper,
    new_cmd,
    unsafe_unwrap,
)
import pytest
from tempfile import (
    TemporaryFile,
)
from typing import (
    Callable,
    IO,
    NoReturn,
)


def _do_not_call() -> NoReturn:
    raise Exception("Cmd action should be only executed on compute phase")


def test_from_cmd() -> None:
    Cmd.from_cmd(_do_not_call)


def test_map() -> None:
    cmd = Cmd.from_cmd(lambda: 44).map(lambda i: i + 5)
    cmd.map(lambda _: _do_not_call())  # type: ignore
    Cmd.from_cmd(_do_not_call).map(lambda _: _)  # type: ignore

    def _verify(num: int) -> None:
        assert num == 49

    with pytest.raises(SystemExit):
        cmd.map(_verify).compute()


def test_bind() -> None:
    cmd = Cmd.from_cmd(lambda: 50)
    cmd2 = Cmd.from_cmd(lambda: 44).bind(lambda i: cmd.map(lambda x: x + i))
    cmd2.bind(lambda _: Cmd.from_cmd(_do_not_call))
    Cmd.from_cmd(_do_not_call).bind(lambda _: cmd)

    def _verify(num: int) -> None:
        assert num == 94

    with pytest.raises(SystemExit):
        cmd2.map(_verify).compute()


def test_apply() -> None:
    cmd = Cmd.from_cmd(lambda: 1)
    wrapped: Cmd[Callable[[int], int]] = Cmd.from_cmd(lambda: lambda x: x + 10)

    dead_end: Cmd[Callable[[int], NoReturn]] = Cmd.from_cmd(
        lambda: lambda _: _do_not_call()  # type: ignore
    )
    ex_falso_quodlibet: Callable[[NoReturn], int] = lambda _: 1
    wrap_no_return: Cmd[Callable[[NoReturn], int]] = Cmd.from_cmd(
        lambda: ex_falso_quodlibet
    )

    cmd.apply(dead_end)
    Cmd.from_cmd(_do_not_call).apply(wrap_no_return)

    def _verify(num: int) -> None:
        assert num == 11

    with pytest.raises(SystemExit):
        cmd.apply(wrapped).map(_verify).compute()


def _print_msg(msg: str, target: IO[str]) -> Cmd[None]:
    return Cmd.from_cmd(lambda: print(msg, file=target))


def test_use_case_1() -> None:
    with pytest.raises(SystemExit):
        with TemporaryFile("r+") as file:

            def _print(msg: str) -> Cmd[None]:
                return _print_msg(msg, file)

            in_val = Cmd.from_cmd(lambda: 245)
            some = in_val.map(lambda i: i + 1).map(str).bind(_print)
            _print("not called")
            pre = _print("Hello World!")
            try:
                pre.bind(lambda _: some).compute()
            except SystemExit as err:
                file.seek(0)
                assert file.readlines() == ["Hello World!\n", "246\n"]
                raise err


def test_new_cmd() -> None:
    state = {}

    def _mutate(val: int) -> None:
        state["temp"] = val

    change_1 = Cmd.from_cmd(lambda: _mutate(99)).map(lambda _: "1")
    change_2 = Cmd.from_cmd(lambda: _mutate(2)).map(lambda _: 2)

    def _action(act: CmdUnwrapper) -> int:
        x = act.unwrap(change_2)
        y = act.unwrap(change_1)
        return x + int(y)

    cmd1 = new_cmd(_action)
    assert state.get("temp") is None
    assert unsafe_unwrap(cmd1) == 3
    assert state["temp"] == 99
