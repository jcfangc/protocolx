from threading import Thread
from typing import Protocol
from unittest.mock import MagicMock, patch

from src.protocolx.definition.type.protocol_sequence import (
    ProtocolSequence,
)


# 示例协议类
class A(Protocol): ...


class B(Protocol): ...


class C(Protocol): ...


class D(Protocol): ...


def assert_sorted_calls(mock_sorted: MagicMock, base: int, delta: int) -> None:
    assert mock_sorted.call_count == base + delta


def assert_set_calls(mock_set: MagicMock, base: int, delta: int) -> None:
    assert mock_set.call_count == base + delta


def assert_hash_calls(mock_hash: MagicMock, base: int, delta: int) -> None:
    assert mock_hash.call_count == base + delta


def test_expensive_operations_called_once() -> None:
    ps = ProtocolSequence([C, A, D, B])

    with (
        patch("builtins.sorted", wraps=sorted) as mock_sorted,
        patch("builtins.set", wraps=set) as mock_set,
        patch("builtins.hash", wraps=hash) as mock_hash,
    ):
        # 记录补丁基线调用次数
        base_sorted = mock_sorted.call_count
        base_set = mock_set.call_count
        base_hash = mock_hash.call_count

        # patch 初始化不应触发额外调用
        assert_set_calls(mock_set, base_set, 0)
        assert_hash_calls(mock_hash, base_hash, 0)

        # __iter__ → 触发一次排序和 set
        _ = list(ps)
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 0)

        # __len__ 不触发重复排序
        _ = len(ps)
        assert_sorted_calls(mock_sorted, base_sorted, 1)  # 仅排序一次
        assert_set_calls(mock_set, base_set, 1)  # 只用一次 set
        assert_hash_calls(mock_hash, base_hash, 0)

        # __getitem__ 不触发重复排序
        _ = ps[0]
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 0)

        # __getitem__(slice) → 返回新 ProtocolSequence，但从 _items 切片，无重复排序
        _ = ps[1:]
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 0)

        # .names → 惰性 name 计算，排序已完成，不重复 set
        _ = ps.names
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 0)

        # __repr__ → 使用 names，仍不重复 set/hash
        _ = repr(ps)
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 0)

        # __hash__ → 第一次触发 hash(names)，再被调用者 hash(ps) 包裹一次，共两次
        _ = hash(ps)
        assert_sorted_calls(mock_sorted, base_sorted, 1)
        assert_set_calls(mock_set, base_set, 1)
        assert_hash_calls(mock_hash, base_hash, 2)  # hash(names) + hash(ps)

        # __eq__ → 比较新实例 ProtocolSequence([A, B, C])，会重新排序一次
        _ = ps == ProtocolSequence([A, B, C])
        assert_sorted_calls(mock_sorted, base_sorted, 2)  # 排序 +1 次
        assert_set_calls(mock_set, base_set, 2)  # set + 1 次（用于新对象排序）
        assert_hash_calls(mock_hash, base_hash, 2)  # 仍然保持 2（新对象未触发 hash）


def test_thread_safety_on_names_and_hash() -> None:
    """
    多线程同时访问 names/hash，不应报错，返回值一致。
    """
    ps = ProtocolSequence([C, A, D, B])
    name_results: list[tuple[str, ...]] = []
    hash_result: list[int] = []

    def access_names() -> None:
        name_results.append(ps.names)

    def access_hash() -> None:
        hash_result.append(hash(ps))

    threads = [Thread(target=access_names) for _ in range(10)] + [
        Thread(target=access_hash) for _ in range(10)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 验证所有结果一致
    name_values = [r for r in name_results]
    hash_values = [r for r in hash_result]
    assert all(n == name_values[0] for n in name_values)
    assert all(h == hash_values[0] for h in hash_values)
