from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.primitive.core import (
    Primitive,
)
from typing import (
    Union,
)

UnfoldedJVal = Union[
    FrozenDict[str, "JsonValue"], FrozenList["JsonValue"], Primitive
]


@dataclass(frozen=True)
class JsonValue:
    _value: UnfoldedJVal

    def unfold(
        self,
    ) -> UnfoldedJVal:
        return self._value
