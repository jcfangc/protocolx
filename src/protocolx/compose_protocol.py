import sys
import types
from types import new_class
from typing import Protocol

from protocolx.definition.type.protocol_sequence import ProtocolSequence
from protocolx.global_var.protocol_cache import (
    get_protocol,
    get_protocol_cache,
    set_protocol,
)


def _ensure_anon_module() -> None:
    """确保虚拟模块 __anon_protocol__ 已注册到 sys.modules。"""
    if "__anon_protocol__" not in sys.modules:
        sys.modules["__anon_protocol__"] = types.ModuleType("__anon_protocol__")


def _get_anon_protocol_class_name(bases: ProtocolSequence, runtime: bool) -> str:
    """
    根据协议组合与 runtime 标志生成唯一 class 名称。
    """
    key = (hash(bases), runtime)
    # 只保留32位，避免过长
    return f"_AnonProtocol_{abs(hash(key)) & 0xFFFF_FFFF:08x}"


def _create_anon_protocol_class(
    class_name: str, bases: ProtocolSequence, runtime: bool
) -> type:
    """
    动态创建 Protocol 匿名组合类，并根据 runtime 标志可选 runtime_checkable。
    """
    proto_cls = new_class(
        class_name, tuple(bases) + (Protocol,), exec_body=lambda ns: None
    )
    if runtime:
        from typing import runtime_checkable

        proto_cls = runtime_checkable(proto_cls)
    proto_cls.__module__ = "__anon_protocol__"
    return proto_cls


def _attach_class_to_anon_module(class_name: str, cls: type) -> None:
    """
    将匿名协议类挂载到虚拟模块 __anon_protocol__，便于 pickle/import 兼容。
    """
    setattr(sys.modules["__anon_protocol__"], class_name, cls)


def compose_protocol(bases: ProtocolSequence, *, runtime: bool = False) -> type:
    """
    动态组合匿名 Protocol，具备可选的 runtime_checkable 能力。
    始终保证结果挂载在虚拟模块 __anon_protocol__ 下，
    以便 pickle / import 能正确解析。
    """
    _ensure_anon_module()
    class_name = _get_anon_protocol_class_name(bases, runtime)
    # 已经存在直接复用
    if class_name in get_protocol_cache():
        protocol_class = get_protocol(name=class_name)
        assert protocol_class is not None
        return protocol_class
    cls = _create_anon_protocol_class(class_name, bases, runtime)
    _attach_class_to_anon_module(class_name, cls)
    set_protocol(name=class_name, cls=cls)
    return cls
