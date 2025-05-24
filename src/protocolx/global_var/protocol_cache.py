import sys
import types
from typing import MutableMapping


def get_anon_protocol_module() -> types.ModuleType:
    if "__anon_protocol__" not in sys.modules:
        sys.modules["__anon_protocol__"] = types.ModuleType("__anon_protocol__")
    return sys.modules["__anon_protocol__"]


def get_protocol_cache() -> MutableMapping[str, type]:
    """返回虚拟模块 __anon_protocol__ 的 __dict__。"""
    return vars(get_anon_protocol_module())


def clear_protocol_cache() -> None:
    """清空虚拟模块 __anon_protocol__ 中的所有协议类。"""
    module = get_anon_protocol_module()
    to_del = [k for k in vars(module) if k.startswith("_AnonProtocol_")]
    for k in to_del:
        delattr(module, k)


def get_protocol(*, name: str) -> type | None:
    """按名称获取协议类对象，不存在返回 None。"""
    module = get_anon_protocol_module()
    return getattr(module, name, None)


def set_protocol(*, name: str, cls: type) -> None:
    """按名称缓存协议类对象。"""
    setattr(get_anon_protocol_module(), name, cls)


def del_protocol(*, name: str) -> None:
    """按名称删除缓存的协议类对象。"""
    module = get_anon_protocol_module()
    if hasattr(module, name):
        delattr(module, name)
