from types import new_class
from typing import Protocol

from src.protocolx.definition.type.protocol_sequence import ProtocolSequence
from src.protocolx.global_var.protocol_cache import _protocol_cache


def compose_protocol(bases: ProtocolSequence, *, runtime: bool = False) -> type:
    """
    只接受 ProtocolSequence，保证协议项按 __name__ 排序且类型安全。
    """
    # 直接使用 ProtocolSequence 的哈希作为 key
    key = hash(bases)  # int 类型
    class_name = f"_AnonProtocol_{abs(key):08x}"  # 取绝对值+16进制字符串，保证命名友好

    # 已经存在直接复用
    if class_name in _protocol_cache:
        return _protocol_cache[class_name]

    cls = new_class(class_name, tuple(bases) + (Protocol,), exec_body=lambda ns: None)

    if runtime:
        from typing import runtime_checkable

        cls = runtime_checkable(cls)

    cls.__module__ = "__anon_protocol__"
    _protocol_cache[class_name] = cls
    return cls
