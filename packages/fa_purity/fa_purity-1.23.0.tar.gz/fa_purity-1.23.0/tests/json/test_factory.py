from fa_purity.frozen import (
    freeze,
)
from fa_purity.json.factory import (
    from_any,
)
from fa_purity.json.value.core import (
    JsonValue,
)


def test_from_any() -> None:
    json_obj = freeze(
        {
            "foo": JsonValue(
                freeze(
                    {
                        "nested": JsonValue(
                            tuple([JsonValue("hi"), JsonValue(99)])
                        ),
                    }
                )
            )
        }
    )
    json_obj_from_raw = from_any({"foo": {"nested": ["hi", 99]}}).unwrap()
    assert json_obj == json_obj_from_raw
