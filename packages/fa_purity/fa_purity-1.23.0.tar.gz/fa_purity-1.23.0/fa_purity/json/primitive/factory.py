from fa_purity.json.errors import (
    invalid_type,
)
from fa_purity.json.errors.invalid_type import (
    InvalidType,
)
from fa_purity.json.primitive.core import (
    NotNonePrimTvar,
)
from fa_purity.result import (
    Result,
)
from typing import (
    Optional,
    Type,
    TypeVar,
)

_T = TypeVar("_T")


def to_primitive(
    raw: _T, prim_type: Type[NotNonePrimTvar]
) -> Result[NotNonePrimTvar, InvalidType]:
    if isinstance(raw, prim_type):
        return Result.success(raw)
    return Result.failure(
        invalid_type.new("to_primitive", str(prim_type), raw)
    )


def to_opt_primitive(
    raw: _T, prim_type: Type[NotNonePrimTvar]
) -> Result[Optional[NotNonePrimTvar], InvalidType]:
    if raw is None or isinstance(raw, prim_type):
        return Result.success(raw)
    return Result.failure(
        invalid_type.new("to_opt_primitive", f"{prim_type} | None", raw)
    )
