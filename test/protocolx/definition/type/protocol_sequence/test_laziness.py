# test_protocol_sequence.py
from typing import Protocol

from hypothesis import given
from hypothesis.strategies import lists, sampled_from

from src.protocolx.definition.type.protocol_sequence import (
    ProtocolSequence,
)


# 定义几个简单的 Protocol 类型用于测试
class A(Protocol):
    def foo(self) -> str: ...


class B(Protocol):
    def bar(self) -> int: ...


class C(Protocol):
    def baz(self) -> float: ...


@given(lists(sampled_from([A, B, C]), min_size=1, max_size=5))
def test_lazy_properties_unaccessed(protocols: list[type]) -> None:
    """
    验证：未访问属性时 _items/_names/_hash 都保持为 None
    """
    ps = ProtocolSequence(protocols)

    assert ps._items is None
    assert ps._names is None
    assert ps._hash is None


@given(lists(sampled_from([A, B, C]), min_size=1, max_size=5))
def test_items_cached_after_iter(protocols: list[type]) -> None:
    """
    测试 __iter__ 访问后，_items 缓存是否正确生成并保持不变。

    步骤：
    1. 初始化时 _items 应为 None。
    2. 第一次迭代后触发 _ensure_sorted，应生成 _items。
    3. 再次迭代时 _items 应保持为同一对象，验证缓存生效。
    """
    ps = ProtocolSequence(protocols)

    # 初始缓存应为空
    assert ps._items is None

    # 第一次访问，触发排序和缓存
    list(ps)
    assert ps._items is not None

    # 缓存结果应一致
    items_before = ps._items
    list(ps)
    assert ps._items is items_before


@given(lists(sampled_from([A, B, C]), min_size=1, max_size=5))
def test_names_cached_after_access(protocols: list[type]) -> None:
    """
    测试 names 属性访问后，_names 缓存是否正确生成并保持不变。

    步骤：
    1. 初始化时 _names 应为 None。
    2. 第一次访问 .names 会触发 _ensure_names → _ensure_sorted。
    3. 再次访问 .names 时，结果应一致，缓存生效。
    """
    ps = ProtocolSequence(protocols)

    assert ps._names is None

    # 第一次访问触发 name 缓存
    _ = ps.names
    assert ps._names is not None

    # 缓存结果应保持不变
    names_before = ps._names
    _ = ps.names
    assert ps._names is names_before


@given(lists(sampled_from([A, B, C]), min_size=1, max_size=5))
def test_hash_cached_after_hash(protocols: list[type]) -> None:
    """
    测试 __hash__ 调用后，_hash 缓存是否正确生成并保持不变。

    步骤：
    1. 初始化时 _hash 应为 None。
    2. 调用 hash() 会触发 _ensure_hash → _ensure_names → _ensure_sorted。
    3. 第二次 hash() 调用应返回相同值，缓存生效。
    """
    ps = ProtocolSequence(protocols)

    assert ps._hash is None

    # 第一次计算 hash
    _ = hash(ps)
    assert ps._hash is not None

    # 缓存结果应保持一致
    hash_before = ps._hash
    _ = hash(ps)
    assert ps._hash == hash_before
