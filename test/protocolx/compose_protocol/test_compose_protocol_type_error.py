from typing import Protocol

import pytest

from src.protocolx.compose_protocol import compose_protocol
from src.protocolx.global_var.protocol_cache import (
    clear_protocol_cache,
)

# ===== 示例协议 =====


class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


def test_non_protocol_sequence_should_raise_type_error() -> None:
    """
    非 ProtocolSequence 输入，应抛出 TypeError。
    """
    clear_protocol_cache()  # ✅ 清空缓存避免污染

    with pytest.raises(TypeError):
        compose_protocol(["not", "a", "protocol"])  # type: ignore[arg-type]
