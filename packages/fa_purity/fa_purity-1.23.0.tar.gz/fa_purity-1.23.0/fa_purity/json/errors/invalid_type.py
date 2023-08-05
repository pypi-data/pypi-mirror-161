from typing import (
    TypeVar,
)

_T = TypeVar("_T")


class _InvalidType(Exception):
    pass


class InvalidType(_InvalidType):
    def __init__(self, obj: _InvalidType) -> None:
        super().__init__(obj)


def new(caller: str, expected: str, item: _T) -> InvalidType:
    draft = _InvalidType(
        f"{caller} expected `{expected}` not `{str(type(item))}`"
    )
    return InvalidType(draft)
