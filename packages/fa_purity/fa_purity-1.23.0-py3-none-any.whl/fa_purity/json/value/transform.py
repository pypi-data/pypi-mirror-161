from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity.frozen import (
    freeze,
    FrozenDict,
    FrozenList,
)
from fa_purity.json.errors import (
    invalid_type,
)
from fa_purity.json.errors.invalid_type import (
    InvalidType,
)
from fa_purity.json.primitive.core import (
    is_primitive,
    NotNonePrimTvar,
    Primitive,
)
from fa_purity.json.primitive.factory import (
    to_primitive as _to_primitive,
)
from fa_purity.json.value.core import (
    JsonValue,
    UnfoldedJVal,
)
from fa_purity.result import (
    Result,
    UnwrapError,
)
from fa_purity.result.core import (
    ResultE,
)
from fa_purity.result.factory import (
    try_get,
)
from fa_purity.result.transform import (
    all_ok,
)
from fa_purity.union import (
    UnionFactory,
)
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

_T = TypeVar("_T")
UnfoldResult = Result[_T, InvalidType]  # type: ignore[misc]


@dataclass(frozen=True)
class Unfolder:
    jval: JsonValue

    @property
    def value(self) -> UnfoldedJVal:
        return self.jval.unfold()

    def get(self, key: str) -> ResultE[JsonValue]:
        return self.to_json().alt(Exception).bind(lambda d: try_get(d, key))

    def uget(self, key: str) -> ResultE[Unfolder]:
        return self.get(key).map(lambda j: Unfolder(j))

    def to_primitive(
        self, prim_type: Type[NotNonePrimTvar]
    ) -> Result[NotNonePrimTvar, InvalidType]:
        return _to_primitive(self.value, prim_type)

    def to_any_primitive(self) -> ResultE[Primitive]:
        if is_primitive(self.value):
            return Result.success(self.value)
        return Result.failure(
            invalid_type.new("to_any_primitive", "Primitive", self.value)
        )

    def to_none(self) -> Result[None, InvalidType]:
        if self.value is None:
            return Result.success(self.value)
        return Result.failure(invalid_type.new("to_none", "None", self.value))

    def to_list(self) -> UnfoldResult[FrozenList[JsonValue]]:
        if isinstance(self.value, tuple):
            return Result.success(self.value)
        return Result.failure(
            invalid_type.new("to_list", "FrozenList[JsonValue]", self.value)
        )

    def to_optional(
        self, transform: Callable[[Unfolder], UnfoldResult[_T]]
    ) -> UnfoldResult[Optional[_T]]:
        _union: UnionFactory[_T, None] = UnionFactory()
        return (
            self.to_none()
            .map(_union.inr)
            .lash(lambda _: transform(self).map(_union.inl))
        )

    def to_opt_list(self) -> UnfoldResult[Optional[FrozenList[JsonValue]]]:
        return self.to_optional(lambda j: j.to_list())

    def to_list_of(
        self, prim_type: Type[NotNonePrimTvar]
    ) -> UnfoldResult[FrozenList[NotNonePrimTvar]]:
        return (
            self.to_list()
            .map(
                lambda l: tuple(
                    _to_primitive(i.unfold(), prim_type) for i in l
                )
            )
            .bind(all_ok)
        )

    def to_unfolder_list(self) -> UnfoldResult[FrozenList[Unfolder]]:
        return self.to_list().map(lambda l: tuple(Unfolder(i) for i in l))

    def to_json(self) -> UnfoldResult[FrozenDict[str, JsonValue]]:
        if isinstance(self.value, FrozenDict):
            return Result.success(self.value)
        return Result.failure(
            invalid_type.new(
                "to_json", "FrozenDict[str, JsonValue]", self.value
            )
        )

    def to_unfolder_dict(self) -> UnfoldResult[FrozenDict[str, Unfolder]]:
        return (
            self.to_json()
            .map(lambda d: {k: Unfolder(v) for k, v in d.items()})
            .map(freeze)
        )

    def to_dict_of(
        self, prim_type: Type[NotNonePrimTvar]
    ) -> UnfoldResult[FrozenDict[str, NotNonePrimTvar]]:
        return (
            self.to_json()
            .map(
                lambda d: tuple(
                    _to_primitive(val.unfold(), prim_type).map(
                        lambda v: (key, v)
                    )
                    for key, val in d.items()
                )
            )
            .bind(lambda x: all_ok(x))
            .map(lambda x: FrozenDict(dict(x)))
        )


def to_raw(jval: JsonValue) -> Union[Dict[str, Any], List[Any], Primitive]:  # type: ignore[misc]
    value = jval.unfold()
    if isinstance(value, tuple):
        return [to_raw(item) for item in value]  # type: ignore[misc]
    if isinstance(value, FrozenDict):
        return {key: to_raw(val) for key, val in value.items()}  # type: ignore[misc]
    return value
