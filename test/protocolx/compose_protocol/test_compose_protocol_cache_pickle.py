import pickle
from typing import Protocol

from src.protocolx.compose_protocol import compose_protocol
from src.protocolx.definition.type.protocol_sequence import ProtocolSequence
from src.protocolx.global_var.protocol_cache import (
    clear_protocol_cache,
    get_protocol,
    get_protocol_cache,
)

# ===== 示例协议 =====


class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


# ===== 测试：相同协议组合（顺序无关）返回同一个类对象 =====


# ===== 测试：不同协议组合返回不同类对象 =====


def test_pickle_unpickle_does_not_create_duplicate() -> None:
    """测试：pickle+unpickle 后类名一致，应仍可命中缓存。"""
    clear_protocol_cache()
    ps = ProtocolSequence([A, B])
    cls = compose_protocol(ps)

    # 模拟跨进程持久化：序列化匿名类
    serialized = pickle.dumps(cls)
    restored = pickle.loads(serialized)

    # 应该是相同类（pickle 会恢复原类引用，而不是构造新类）
    assert restored is cls
    # 应在缓存中，未发生重复创建
    assert restored.__name__ in get_protocol_cache()
    protocol_class = get_protocol(name=restored.__name__)
    assert protocol_class is not None
    assert protocol_class is restored


def test_reimport_simulation_hits_cache() -> None:
    """测试：即使重新组合协议，也不重复创建类对象。"""
    clear_protocol_cache()
    ps1 = ProtocolSequence([A, B])
    cls1 = compose_protocol(ps1)

    # 模拟重新组合（顺序不同）
    ps2 = ProtocolSequence([B, A])
    cls2 = compose_protocol(ps2)

    assert cls1 is cls2
    assert cls1.__name__ == cls2.__name__
    assert cls1.__name__ in get_protocol_cache()
