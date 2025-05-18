from typing import (
    Iterator,
    Optional,
    Sequence,
    SupportsIndex,
    Union,
    overload,
)


class ProtocolSequence(Sequence[type]):
    """
    专属的 Protocol 类型有序集合，只允许 Protocol 子类项。
    排序、名字和哈希全部惰性计算，真正需要时才会执行。
    """

    def __init__(self, items: Sequence[type]) -> None:
        self._original_items: tuple[type, ...] = tuple(items)
        self._items: Optional[tuple[type, ...]] = None
        self._names: Optional[tuple[str, ...]] = None
        self._hash: Optional[int] = None

    def _ensure_sorted(self) -> None:
        if self._items is None:
            for b in self._original_items:
                if not isinstance(b, type):
                    raise TypeError(f"{b} is not a type")
                if not getattr(b, "_is_protocol", False):
                    raise TypeError(f"{b} is not a subclass of Protocol")
            self._items = tuple(
                sorted(set(self._original_items), key=lambda cls: cls.__name__)
            )

    def _ensure_names(self) -> None:
        if self._names is None:
            self._ensure_sorted()
            assert self._items is not None
            self._names = tuple(cls.__name__ for cls in self._items)

    def _ensure_hash(self) -> None:
        if self._hash is None:
            self._ensure_names()
            self._hash = hash(self._names)

    def __iter__(self) -> Iterator[type]:
        self._ensure_sorted()
        assert self._items is not None
        return iter(self._items)

    def __len__(self) -> int:
        self._ensure_sorted()
        assert self._items is not None
        return len(self._items)

    @overload
    def __getitem__(self, index: SupportsIndex) -> type: ...

    @overload
    def __getitem__(self, index: slice) -> "ProtocolSequence": ...

    def __getitem__(
        self, index: SupportsIndex | slice
    ) -> Union[type, "ProtocolSequence"]:
        self._ensure_sorted()
        assert self._items is not None
        if isinstance(index, slice):
            return ProtocolSequence(self._items[index])
        return self._items[index]

    def __repr__(self) -> str:
        self._ensure_names()
        assert self._names is not None
        names = ", ".join(self._names)
        return f"ProtocolSequence({names})"

    def __hash__(self) -> int:
        self._ensure_hash()
        assert self._hash is not None
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProtocolSequence):
            return False
        return self.names == other.names

    @property
    def names(self) -> tuple[str, ...]:
        self._ensure_names()
        assert self._names is not None
        return self._names
