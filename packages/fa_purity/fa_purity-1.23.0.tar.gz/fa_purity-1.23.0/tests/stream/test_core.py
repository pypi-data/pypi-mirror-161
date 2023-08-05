from fa_purity.cmd import (
    unsafe_unwrap,
)
from fa_purity.cmd.core import (
    Cmd,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.factory import (
    from_flist,
    from_range,
)
from fa_purity.stream.core import (
    Stream,
)
from fa_purity.stream.factory import (
    from_piter,
)
from tests.stream._utils import (
    assert_different_iter,
    rand_int,
)
from typing import (
    Callable,
)


def test_map() -> None:
    items = from_range(range(10)).map(lambda _: rand_int())
    stm = from_piter(items).map(lambda i: i + 1)
    assert_different_iter(stm)


def test_chunked() -> None:
    items = from_range(range(10)).map(lambda _: rand_int())
    stm = from_piter(items).chunked(2)
    assert_different_iter(stm)


def test_find_first() -> None:
    items = from_piter(from_range(range(10)).map(lambda _: rand_int()))
    assert_different_iter(items)
    assert unsafe_unwrap(items.find_first(lambda n: n >= 0)).unwrap() >= 0
    assert unsafe_unwrap(items.find_first(lambda n: n > 9999)) == Maybe.empty()


def test_bind() -> None:
    items = from_piter(
        from_range(range(5)).map(lambda i: Cmd.from_cmd(lambda: i))
    )
    items2: Callable[[int], Stream[int]] = lambda n: from_piter(
        from_flist((n, n)).map(lambda i: Cmd.from_cmd(lambda: i))
    )
    expected = (0, 0, 1, 1, 2, 2, 3, 3, 4, 4)
    result = items.bind(items2)
    assert_different_iter(result)
    assert unsafe_unwrap(result.to_list()) == expected
