from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.errors import (
    invalid_type,
)
from fa_purity.json.errors.invalid_type import (
    InvalidType,
)
from fa_purity.json.primitive import (
    factory as prim_factory,
)
from fa_purity.json.primitive.core import (
    is_primitive,
    Primitive,
)
from fa_purity.json.value.core import (
    JsonValue,
)
from fa_purity.result import (
    Result,
)
from fa_purity.utils import (
    raise_exception,
)
from typing import (
    Dict,
    List,
    TypeVar,
    Union,
)

_T = TypeVar("_T")


def from_list(raw: Union[List[Primitive], FrozenList[Primitive]]) -> JsonValue:
    return JsonValue(tuple(JsonValue(item) for item in raw))


def from_dict(
    raw: Union[Dict[str, Primitive], FrozenDict[str, Primitive]]
) -> JsonValue:
    return JsonValue(
        FrozenDict({key: JsonValue(val) for key, val in raw.items()})
    )


def from_any(raw: _T) -> Result[JsonValue, InvalidType]:
    if is_primitive(raw):
        return Result.success(JsonValue(raw))
    if isinstance(raw, (FrozenDict, dict)):
        try:
            json_dict = FrozenDict(
                {
                    prim_factory.to_primitive(key, str)
                    .alt(raise_exception)
                    .unwrap(): from_any(val)
                    .alt(raise_exception)
                    .unwrap()
                    for key, val in raw.items()
                }
            )
            return Result.success(JsonValue(json_dict))
        except InvalidType as err:
            return Result.failure(err)
    if isinstance(raw, list):
        try:
            json_list = tuple(
                from_any(item).alt(raise_exception).unwrap() for item in raw
            )
            return Result.success(JsonValue(json_list))
        except InvalidType as err:
            return Result.failure(err)
    return Result.failure(invalid_type.new("from_any", "UnfoldedJVal", raw))
