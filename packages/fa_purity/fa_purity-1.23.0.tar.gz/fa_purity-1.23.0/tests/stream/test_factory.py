from fa_purity.pure_iter.factory import (
    from_range,
)
from fa_purity.stream.factory import (
    from_piter,
)
from tests.stream._utils import (
    assert_different_iter,
    rand_int,
)


def test_from_piter() -> None:
    items = from_range(range(10)).map(lambda _: rand_int())
    stm = from_piter(items)
    assert_different_iter(stm)
