from typing import Protocol

from hypothesis import given
from hypothesis.strategies import lists, sampled_from

from src.protocolx.definition.type.protocol_sequence import (
    ProtocolSequence,
)

# ==== 示例协议定义 ====


class X(Protocol):
    def x(self) -> None: ...


class Y(Protocol):
    def y(self) -> None: ...


class Z(Protocol):
    def z(self) -> None: ...


@given(lists(sampled_from([Y, X, Z]), min_size=1, max_size=5))
def test_sorted_correctly(protocols: list[type]) -> None:
    """
    测试：ProtocolSequence 中协议应按名称排序。
    """
    ps = ProtocolSequence(protocols)
    sorted_names = sorted(cls.__name__ for cls in set(protocols))
    actual_names = [cls.__name__ for cls in ps]
    assert actual_names == sorted_names


@given(lists(sampled_from([Y, X, Z]), min_size=1, max_size=5))
def test_iteration_yields_sorted(protocols: list[type]) -> None:
    """
    测试：迭代 ProtocolSequence 返回的应是排序后的类型列表。
    """
    ps = ProtocolSequence(protocols)
    expected = sorted(set(protocols), key=lambda cls: cls.__name__)
    actual = list(ps)
    assert actual == expected


@given(lists(sampled_from([Y, X, Z]), min_size=1, max_size=5))
def test_length_is_correct(protocols: list[type]) -> None:
    """
    测试：len() 返回的长度应等于去重后的协议类数量。
    """
    ps = ProtocolSequence(protocols)
    assert len(ps) == len(set(ps))  # 类型对象唯一，集合去重


@given(lists(sampled_from([Y, X, Z]), min_size=1, max_size=5))
def test_index_access_returns_expected(protocols: list[type]) -> None:
    """
    测试：通过索引访问，返回值应与排序后结果一致。
    """
    ps = ProtocolSequence(protocols)
    expected = sorted(set(protocols), key=lambda cls: cls.__name__)
    for i in range(len(expected)):
        assert ps[i] is expected[i]
