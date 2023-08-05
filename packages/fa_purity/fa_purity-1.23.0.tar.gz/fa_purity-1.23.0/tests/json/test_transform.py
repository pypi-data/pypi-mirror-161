from fa_purity.json.factory import (
    from_any,
)
from fa_purity.json.transform import (
    dumps,
)

test_data = from_any({"foo": {"nested": ["hi", 99]}}).unwrap()


def test_dumps() -> None:
    assert dumps(test_data).replace(
        " ", ""
    ) == '{"foo": {"nested": ["hi", 99]} }'.replace(" ", "")
