from typing import Protocol

import pytest

from src.protocolx.definition.type.protocol_sequence import (
    ProtocolSequence,
)


# 示例协议
class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


# === 空输入测试 ===


def test_empty_protocol_sequence_should_work() -> None:
    """
    测试：空输入是合法的，返回空的 ProtocolSequence。
    """
    ps = ProtocolSequence([])

    # list 展开应为空
    assert list(ps) == []

    # 长度应为 0
    assert len(ps) == 0

    # names 应为 ()
    assert ps.names == ()

    # __repr__
    assert repr(ps) == "ProtocolSequence()"

    # 可哈希（等价于 hash(())）
    assert hash(ps) == hash(())
    assert isinstance(hash(ps), int)

    # 迭代应抛出 StopIteration
    it = iter(ps)
    with pytest.raises(StopIteration):
        next(it)


# === 单元素测试 ===


def test_single_element_behavior() -> None:
    """
    测试：单个 Protocol 输入时，排序、长度、names、迭代等行为。
    """
    ps = ProtocolSequence([B])

    assert len(ps) == 1
    assert list(ps) == [B]
    assert ps.names == ("B",)
    assert repr(ps) == "ProtocolSequence(B)"
    assert hash(ps) == hash(("B",))


# === 多元素测试 ===


def test_multiple_protocols_behavior() -> None:
    """
    测试：多个 Protocol 输入时，是否正确排序并展现各行为。
    """
    ps = ProtocolSequence([C, A, B])  # 原始顺序 CAB → 应排序为 A, B, C

    assert len(ps) == 3
    assert ps.names == ("A", "B", "C")
    assert list(ps) == [A, B, C]
    assert ps[0] == A and ps[2] == C
    assert repr(ps) == "ProtocolSequence(A, B, C)"
    assert isinstance(hash(ps), int)


# === 不合法类型测试 ===


def test_non_protocol_type_should_raise() -> None:
    """
    测试：非 Protocol 类型输入是否抛出 TypeError。
    """

    class NotAProtocol:
        pass

    ps = ProtocolSequence([A, NotAProtocol])  # NotAProtocol 不继承自 Protocol
    with pytest.raises(TypeError, match="not a subclass of Protocol"):
        list(ps)  # 强制触发 _ensure_sorted，触发类型检查


def test_non_type_object_should_raise() -> None:
    """
    测试：非类型对象（如字符串）作为输入项，访问时应抛出 TypeError。
    """
    ps = ProtocolSequence([A, "not a type"])  # 初始化阶段不报错
    with pytest.raises(TypeError, match="not a type"):
        list(ps)  # 强制触发 _ensure_sorted，触发类型检查


# === 重复元素测试 ===


def test_duplicate_protocols_are_preserved() -> None:
    """
    测试：输入中重复的协议类不应保留，并按类名排序。
    """
    ps = ProtocolSequence([B, A, B])
    assert list(ps) == [A, B]  # 因为 A < B，且不保留重复
    assert ps.names == ("A", "B")
