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


# === 示例协议定义 ===


class Alpha(Protocol):
    def a(self) -> None: ...


class Beta(Protocol):
    def b(self) -> None: ...


class Gamma(Protocol):
    def c(self) -> None: ...


@given(lists(sampled_from([Alpha, Beta, Gamma]), min_size=1, max_size=5))
def test_repr_shows_sorted_names(protocols: list[type]) -> None:
    """
    测试：__repr__ 的输出应包含排序后的协议名称。
    """
    ps = ProtocolSequence(protocols)
    sorted_names = sorted(cls.__name__ for cls in protocols)
    for name in sorted_names:
        assert name in repr(ps)
    assert repr(ps).startswith("ProtocolSequence(")


@given(lists(sampled_from([Alpha, Beta, Gamma]), min_size=1, max_size=5))
def test_hash_consistent_with_sorted_names(protocols: list[type]) -> None:
    """
    测试：__hash__ 应等于 hash(排序后的名称元组)。
    """
    ps = ProtocolSequence(protocols)
    expected_hash = hash(tuple(sorted(set(cls.__name__ for cls in protocols))))
    assert hash(ps) == expected_hash


@given(lists(sampled_from([Alpha, Beta, Gamma]), min_size=1, max_size=5))
def test_equality_based_on_names(protocols: list[type]) -> None:
    """
    测试：两个 ProtocolSequence 对象名称一致则相等，顺序无关。
    """
    ps1 = ProtocolSequence(protocols)
    ps2 = ProtocolSequence(list(reversed(protocols)))
    assert ps1 == ps2
    assert hash(ps1) == hash(ps2)


def test_equality_with_non_protocolsequence_object() -> None:
    """
    测试：与非 ProtocolSequence 对象比较应返回 False。
    """
    ps = ProtocolSequence([Alpha, Beta])
    assert ps != ["Alpha", "Beta"]
    assert ps is not None
    assert ps != object()


@given(lists(sampled_from([Alpha, Beta, Gamma]), min_size=1, max_size=5))
def test_names_are_sorted_class_names(protocols: list[type]) -> None:
    """
    测试：.names 返回排序后的类名元组，与 __name__ 排序一致。
    """
    ps = ProtocolSequence(protocols)

    # 预期类名列表（已排序）
    expected_names = tuple(sorted(set(cls.__name__ for cls in protocols)))

    # 实际返回的 names
    actual_names = ps.names

    # 验证内容正确
    assert actual_names == expected_names

    # 验证 names 与迭代项的 __name__ 一致
    iter_names = tuple(cls.__name__ for cls in ps)
    assert actual_names == iter_names
