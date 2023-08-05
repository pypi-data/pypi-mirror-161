from fa_purity.pure_iter.factory import (
    from_flist,
    from_range,
    infinite_gen,
    infinite_range,
)
from tests.pure_iter._utils import (
    assert_immutability,
    assert_immutability_inf,
    to_tuple,
)


def test_flist() -> None:
    items = tuple(range(10))
    assert_immutability(from_flist(items))


def test_range() -> None:
    assert_immutability(from_range(range(10)))


def test_inf_range() -> None:
    assert_immutability_inf(infinite_range(3, 5))


def test_infinite_gen() -> None:
    items = infinite_gen(lambda x: x + 1, 0)
    assert_immutability_inf(items)
    assert to_tuple(items, 10) == tuple(range(10))
