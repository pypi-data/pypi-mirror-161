from fa_purity.frozen import (
    FrozenDict,
)


def test_hashable_dict() -> None:
    a = FrozenDict({"test": 99})
    b = FrozenDict({"test": 99})
    assert frozenset([a, b]) == frozenset([a])
