import inspect
from typing import Callable, Type

from definition.enum.check_status import CheckStatus
from definition.enum.protocol_meta_key import ProtocolMetaKey
from definition.protocolx import Protocolx
from protocolx.internal import (
    _check_method_exists,
    _get_class_methods,
    _get_protocol_meta,
    _get_protocol_methods,
    _get_protocol_prefix,
    _inject_default_if_available,
    _report_check_result,
)


def _check_and_inject_protocol(
    proto: Type[Protocolx], cls: Type, cls_methods: dict[str, Callable]
) -> None:
    """
    检查并注入指定协议的方法实现。

    该函数会：
    - 提取给定协议的元信息（如默认实现类、是否允许使用默认方法）；
    - 遍历协议中定义的所有方法；
    - 检查目标类中是否已实现每个方法；
    - 若未实现，且协议允许默认实现，则尝试从默认实现类注入；
    - 打印每个方法的检查状态（已实现、注入、缺失、签名不一致）。


    Args:
        proto (Type[Protocolx]): 要检查的协议类，必须继承自 Protocolx 并在内部定义 __protocolx__ 元信息字段。
        cls (Type): 被检查的目标类。
        cls_methods (dict[str, Callable]): 目标类中定义的所有可调用方法的映射（已由上层函数提前提取）。
    """
    meta = _get_protocol_meta(proto)
    defaults_provider = meta.get(ProtocolMetaKey.DEFAULTS)
    use_default: bool = meta.get(ProtocolMetaKey.USE_DEFAULT, True)

    proto_name = proto.__name__
    prefix = _get_protocol_prefix(proto)
    proto_methods = _get_protocol_methods(proto)

    print(f"\n✅ Implements {proto_name} (prefix: '{prefix}'):")

    for method_name, proto_method in proto_methods.items():
        expected_name = prefix + method_name
        exists, signature_ok = _check_method_exists(
            expected_name, proto_method, cls_methods
        )

        if exists:
            if signature_ok:
                _report_check_result(expected_name, CheckStatus.OK)
            else:
                proto_sig = inspect.signature(proto_method)
                impl_sig = inspect.signature(cls_methods[expected_name])
                _report_check_result(
                    expected_name, CheckStatus.MISMATCH, proto_sig, impl_sig
                )
        elif use_default and _inject_default_if_available(
            cls, expected_name, defaults_provider
        ):
            _report_check_result(expected_name, CheckStatus.INJECTED)
        else:
            _report_check_result(expected_name, CheckStatus.MISSING)


def implements(protocols: list[Type[Protocolx]]) -> Callable[[Type], Type]:
    """
    类装饰器：用于声明一个类实现了哪些协议（Protocolx），并自动进行校验与默认实现注入。

    Args:
        protocols (list[Type[Protocolx]]):
            要实现的协议类列表。
                - 每个协议必须是继承自 `Protocolx` 的类。
                - 协议内部应包含 `__protocolx__` 属性来指定默认实现和配置选项。

    Returns:
        Callable[[Type], Type]:
            装饰器函数，接收目标类并返回经过检查后的类对象。
    """

    def decorator(cls: Type) -> Type:
        print(f"\n🔍 Checking implementation for class '{cls.__name__}'")

        # 提取目标类中所有可调用的方法
        cls_methods = _get_class_methods(cls)

        # 遍历每个协议，执行检查和必要的默认注入
        for proto in protocols:
            _check_and_inject_protocol(proto, cls, cls_methods)

        # 返回原始类（已可能被注入默认方法）
        return cls

    return decorator
