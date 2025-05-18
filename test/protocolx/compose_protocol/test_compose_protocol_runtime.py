from typing import Protocol

import pytest

from src.protocolx.compose_protocol import compose_protocol
from src.protocolx.definition.type.protocol_sequence import ProtocolSequence
from src.protocolx.global_var.protocol_cache import _protocol_cache

# ===== 示例协议 =====


class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


def test_compose_protocol_with_runtime_enabled() -> None:
    _protocol_cache.clear()  # ✅ 清空缓存避免污染

    ps = ProtocolSequence([A, B])
    cls = compose_protocol(ps, runtime=True)

    class Impl:
        pass

    try:
        _ = isinstance(Impl(), cls)
        _ = issubclass(Impl, cls)
    except TypeError:
        pytest.fail("runtime=True 的匿名类应支持 isinstance / issubclass 检查")


def test_compose_protocol_with_runtime_disabled() -> None:
    """
    测试：当 runtime=False 时，不具备 __runtime_protocol__ 属性，
    运行时检查 isinstance / issubclass 会抛出 TypeError。
    """
    _protocol_cache.clear()  # ✅ 清空缓存避免污染

    ps = ProtocolSequence([A, B])
    cls = compose_protocol(ps, runtime=False)

    # 不具备 runtime_checkable 标志
    assert not hasattr(cls, "__runtime_protocol__")

    # 不允许使用 isinstance / issubclass
    class Impl:
        pass

    with pytest.raises(TypeError):
        isinstance(Impl(), cls)

    with pytest.raises(TypeError):
        issubclass(Impl, cls)
