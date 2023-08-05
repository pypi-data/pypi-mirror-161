from dataclasses import (
    dataclass,
)
from typing import (
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    overload,
    Tuple,
    TypeVar,
    Union,
)

_K = TypeVar("_K")
_V = TypeVar("_V")
_T = TypeVar("_T")

FrozenList = Tuple[_T, ...]  # type: ignore[misc]


@dataclass(frozen=True)
class _FrozenDict(Generic[_K, _V]):
    _dict: Dict[_K, _V]


class FrozenDict(Mapping[_K, _V], _FrozenDict[_K, _V]):
    def __init__(self, dictionary: Dict[_K, _V]):
        super().__init__(dictionary.copy())

    def __getitem__(self, key: _K) -> _V:
        return self._dict[key]

    def __iter__(self) -> Iterator[_K]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self._dict}"

    def __hash__(self) -> int:
        return hash(frozenset(self._dict.items()))


def chain(unchained: FrozenList[FrozenList[_T]]) -> FrozenList[_T]:
    return tuple(item for items in unchained for item in items)


@overload
def freeze(target: List[_T]) -> FrozenList[_T]:
    pass


@overload
def freeze(target: Dict[_K, _V]) -> FrozenDict[_K, _V]:
    pass


def freeze(
    target: Union[List[_T], Dict[_K, _V]]
) -> Union[FrozenList[_T], FrozenDict[_K, _V]]:
    if isinstance(target, list):
        return tuple(target)
    return FrozenDict(target)


@overload
def unfreeze(target: FrozenList[_T]) -> List[_T]:
    pass


@overload
def unfreeze(target: FrozenDict[_K, _V]) -> Dict[_K, _V]:
    pass


def unfreeze(
    target: Union[FrozenList[_T], FrozenDict[_K, _V]]
) -> Union[List[_T], Dict[_K, _V]]:
    if isinstance(target, FrozenDict):
        return {k: v for k, v in target.items()}
    return [i for i in target]
