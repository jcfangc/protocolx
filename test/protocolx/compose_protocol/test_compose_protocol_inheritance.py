from typing import Protocol, runtime_checkable

from hypothesis import given
from hypothesis.strategies import lists, sampled_from

from src.protocolx.compose_protocol import compose_protocol
from src.protocolx.definition.type.protocol_sequence import ProtocolSequence
from src.protocolx.global_var.protocol_cache import (
    clear_protocol_cache,
)

# ===== 示例协议 =====


class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


@runtime_checkable
class P1(Protocol):
    def m1(self) -> int: ...


@runtime_checkable
class P2(Protocol):
    def m2(self, x: str) -> str: ...


@runtime_checkable
class P3(Protocol):
    def m3(self, y: float) -> int: ...


ALL_PROTOCOLS: list[type] = [P1, P2, P3]


@given(sampled_from(ALL_PROTOCOLS))
def test_single_protocol_behavior(proto: type) -> None:
    """
    如果 ProtocolSequence 只包含一个协议，
    compose_protocol 返回的匿名类应与该协议完全等价：
      * issubclass(Anonymous, proto) 为 True
      * isinstance(obj, Anonymous) 与 proto 相同行为
    """
    clear_protocol_cache()  # ✅ 清空缓存避免污染

    seq = ProtocolSequence([proto])
    anon_cls = compose_protocol(seq, runtime=True)

    # 匿名类本身仍是 Protocol 子类
    assert issubclass(anon_cls, Protocol)

    # 与原协议等价（是其子类）
    assert issubclass(anon_cls, proto)  # type: ignore

    # isinstance 检查 —— 这里直接构造一个最简单的占位实现
    class Dummy:
        pass

    # 不实现协议自然返回 False，但不应抛 TypeError
    assert isinstance(Dummy(), anon_cls) is False


@given(lists(sampled_from(ALL_PROTOCOLS), min_size=2, max_size=3))
def test_multi_protocol_behavior(protocols: list[type]) -> None:
    clear_protocol_cache()  # ✅ 清空缓存避免污染

    seq = ProtocolSequence(protocols)
    anon = compose_protocol(seq, runtime=True)

    # 同时是所有协议的子类
    for p in protocols:
        assert issubclass(anon, p)
