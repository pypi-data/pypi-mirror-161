from __future__ import (
    annotations,
)

from deprecated import (
    deprecated,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.errors import (
    invalid_type,
)
from fa_purity.json.primitive.core import (
    Primitive,
)
from fa_purity.json.value import (
    factory as jval_factory,
)
from fa_purity.json.value.core import (
    JsonValue,
    UnfoldedJVal,
)
from fa_purity.json.value.transform import (
    Unfolder,
    UnfoldResult,
)
from fa_purity.result import (
    Result,
)
from fa_purity.utils import (
    raise_exception,
)
import simplejson
from typing import (
    Any,
    cast,
    Dict,
    IO as IO_FILE,
    TypeVar,
)

_T = TypeVar("_T")
JsonObj = FrozenDict[str, JsonValue]


class UnexpectedResult(Exception):
    pass


def from_any(raw: _T) -> UnfoldResult[JsonObj]:
    return jval_factory.from_any(raw).bind(lambda j: Unfolder(j).to_json())


@deprecated("use `from_unfolded_dict` instead; function arg is mutable and not generic enough")  # type: ignore[misc]
def from_prim_dict(raw: Dict[str, Primitive]) -> JsonObj:
    return FrozenDict({key: JsonValue(val) for key, val in raw.items()})


def from_unfolded_dict(raw: FrozenDict[str, UnfoldedJVal]) -> JsonObj:
    return FrozenDict({key: JsonValue(val) for key, val in raw.items()})


def loads(raw: str) -> UnfoldResult[JsonObj]:
    raw_json = cast(Dict[str, Any], simplejson.loads(raw))  # type: ignore[misc]
    return from_any(raw_json)  # type: ignore[misc]


def load(raw: IO_FILE[str]) -> UnfoldResult[JsonObj]:
    raw_json = cast(Dict[str, Any], simplejson.load(raw))  # type: ignore[misc]
    return from_any(raw_json)  # type: ignore[misc]


def json_list(raw: _T) -> UnfoldResult[FrozenList[JsonObj]]:
    try:
        if isinstance(raw, (list, tuple)):
            return Result.success(
                tuple(
                    from_any(item).alt(raise_exception).unwrap()
                    for item in raw
                )
            )
        return Result.failure(invalid_type.new("json_list", "List|Tuple", raw))
    except invalid_type.InvalidType as err:
        return Result.failure(err)
