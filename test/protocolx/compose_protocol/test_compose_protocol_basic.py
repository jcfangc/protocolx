import re
from itertools import permutations
from typing import Protocol

from hypothesis import given
from hypothesis.strategies import lists, sampled_from

from src.protocolx.compose_protocol import compose_protocol
from src.protocolx.definition.type.protocol_sequence import ProtocolSequence
from src.protocolx.global_var.protocol_cache import _protocol_cache

# ===== 示例协议 =====


class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


@given(lists(sampled_from([A, B, C]), min_size=1, max_size=3))
def test_same_combination_returns_same_class(protocols: list[type]) -> None:
    """
    测试：相同的协议组合（不同顺序）返回同一个匿名 Protocol 类对象（缓存命中）。
    """
    _protocol_cache.clear()  # ✅ 清空缓存避免污染

    ps1 = ProtocolSequence(protocols)
    cls1 = compose_protocol(ps1)

    # 随机打乱顺序重新组合
    for perm in permutations(protocols):
        ps2 = ProtocolSequence(perm)
        cls2 = compose_protocol(ps2)
        assert cls1 is cls2, f"Cache miss for permutation {perm}"


def test_different_combinations_return_different_classes() -> None:
    """
    测试：不同的协议组合返回不同的匿名 Protocol 类对象。
    """
    _protocol_cache.clear()  # ✅ 清空缓存避免污染

    # A + B
    cls1 = compose_protocol(ProtocolSequence([A, B]))
    # A + C
    cls2 = compose_protocol(ProtocolSequence([A, C]))
    # A + B + C
    cls3 = compose_protocol(ProtocolSequence([A, B, C]))
    # B + C
    cls4 = compose_protocol(ProtocolSequence([B, C]))

    # 每组都应该是不同的类对象
    assert cls1 is not cls2
    assert cls1 is not cls3
    assert cls1 is not cls4
    assert cls2 is not cls3
    assert cls2 is not cls4
    assert cls3 is not cls4


def test_composed_protocol_class_properties() -> None:
    """
    测试：compose_protocol 返回匿名类属性符合预期：
    - 是 type 且 Protocol 的子类
    - __name__ 符合命名规则
    - __module__ 正确
    - 名称中的 hash 来源一致
    """
    _protocol_cache.clear()

    ps = ProtocolSequence([A, B])
    runtime_flag = False
    result = compose_protocol(ps, runtime=runtime_flag)

    # 是一个类
    assert isinstance(result, type)
    # 是 Protocol 的子类
    assert issubclass(result, Protocol)
    # 模块名正确
    assert result.__module__ == "__anon_protocol__"

    # 类名以 _AnonProtocol_ 开头 + 8位十六进制
    assert re.fullmatch(r"_AnonProtocol_[0-9a-f]{8}", result.__name__), result.__name__

    # 验证类名中的 hash 部分是否正确来源于 hash((hash(ps), runtime))
    expected_key = (hash(ps), runtime_flag)
    expected_suffix = f"{abs(hash(expected_key)) & 0xFFFF_FFFF:08x}"
    assert result.__name__.endswith(expected_suffix), (
        f"{result.__name__=} 不以预期 hash 后缀结尾 {expected_suffix=}"
    )
