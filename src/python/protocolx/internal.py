import inspect
from types import FunctionType, MethodType
from typing import Any, Callable, Optional, Type

from src.python.definition.const.protocol_meta import PROTOCOL_META_ATTR
from src.python.definition.enum.check_status import CheckStatus
from src.python.definition.protocolx import Protocolx


def _get_class_methods(cls: Type) -> dict[str, Callable]:
    """
    提取类中所有声明为可调用的成员方法（即函数或静态方法等）。
    该函数会遍历类的 `__dict__`（等价于 `vars(cls)`），筛选出所有值为可调用对象的条目。

    Args:
        cls (Type):
            需要提取方法的类对象。

    Returns:
        dict[str, Callable]:
            一个字典，键是方法名，值是该类定义的可调用成员（如实例方法、类方法、静态方法）。
            不包含继承自父类但未重写的方法。
    """

    methods = {}
    for name, member in vars(cls).items():
        if isinstance(member, (FunctionType, MethodType)):  # 普通函数或实例方法
            methods[name] = member
        elif isinstance(member, staticmethod):  # 静态方法
            methods[name] = member.__func__
        elif isinstance(member, classmethod):  # 类方法
            methods[name] = member.__func__
    return methods


def _get_protocol_methods(proto: Type[Protocolx]) -> dict[str, Callable]:
    """
    提取协议类中声明的所有公开方法（即非私有、非魔术方法的可调用成员）。
    该函数用于获取协议中定义的方法签名，以用于实现类的对照检查。

    Args:
        proto (Type[Protocolx]):
            一个协议类，必须继承自 `Protocolx`，应为 PEP 544 格式的结构化接口。

    Returns:
        dict[str, Callable]:
            一个字典，键为方法名，值为可调用对象（函数对象），不包含私有方法（以 "_" 开头）。
    """
    return {
        name: member
        for name, member in vars(proto).items()
        if callable(member) and not name.startswith("_")
    }


def _get_protocol_prefix(proto: Type) -> str:
    """
    根据协议类名生成方法前缀。

    协议方法在实现类中使用 `{prefix}{method_name}` 规则进行绑定：
    - 默认使用协议类名去掉首字母 `I`（如 IGreeter → greeter_）；
    - 保证多个协议组合时命名空间隔离，避免方法名冲突。

    Args:
        proto (Type):
            协议类类型，建议命名以大写字母 `I` 开头（如 IGreeter）。

    Returns:
        str:
            自动推导的前缀字符串，例如 'greeter_'。
    """
    return proto.__name__.lower().removeprefix("i") + "_"


def _get_protocol_meta(proto: Type[Protocolx]) -> dict[str, Any]:
    """
    获取协议类上绑定的元信息配置。

    协议元信息应定义为类属性 `__protocolx__`，用于描述：
    - 是否允许使用默认实现；
    - 默认方法提供者对象（如类或模块）；
    - 其他自定义扩展字段。

    Args:
        proto (Type[Protocolx]):
            协议类，需继承自 Protocolx 并定义 `__protocolx__` 属性。

    Returns:
        dict[str, Any]:
            包含协议元信息的字典，若协议未定义元信息则返回空字典。
    """
    return getattr(proto, PROTOCOL_META_ATTR, {})


def _check_method_exists(
    expected_name: str,
    proto_method: Callable,
    cls_methods: dict[str, Callable],
) -> tuple[bool, bool]:
    """
    检查实现类中是否存在指定方法，且其签名是否与协议定义一致。

    Args:
        expected_name (str):
            在实现类中期望的方法名（通常是由协议名生成的前缀加方法名，例如 `greeter_greet`）。

        proto_method (Callable):
            协议中定义的方法对象，用于提取其签名。

        cls_methods (dict[str, Callable]):
            实现类中所有方法的字典（通常由 `_get_class_methods` 获取）。

    Returns:
        tuple[bool, bool]:
            - 第一个值表示该方法是否存在于类中；
            - 第二个值表示方法签名是否与协议中定义的一致（仅在存在时才有意义）。
    """
    if expected_name not in cls_methods:
        return False, False

    proto_sig = inspect.signature(proto_method)
    impl_sig = inspect.signature(cls_methods[expected_name])
    return True, proto_sig == impl_sig


def _inject_default_if_available(
    cls: Type,
    method_name: str,
    defaults_provider: Any,
) -> bool:
    """
    尝试将默认实现注入到目标类中。

    如果 `defaults_provider` 中存在名为 `method_name` 的方法，
    则将其绑定到目标类 `cls` 上，并返回 True；否则什么都不做并返回 False。

    ⚠️ 注：该注入在类级别完成，使用的是 `method.__get__(cls)` 的绑定方式，
    可保证方法拥有正确的上下文（类似实例方法）。

    Args:
        cls (Type):
            要注入方法的目标类。

        method_name (str):
            期望注入的方法名（通常为协议名派生后的名称，如 `greeter_greet`）。

        defaults_provider (Any):
            提供默认实现的方法容器，可以是类、模块、对象等。

    Returns:
        bool:
            如果注入成功，返回 True；否则返回 False。
    """
    if defaults_provider and hasattr(defaults_provider, method_name):
        method = getattr(defaults_provider, method_name, None)

        # 注入方法到类中，保证方法不会覆盖类中已有的同名方法
        if callable(method) and method_name not in vars(cls):
            setattr(cls, method_name, method.__get__(cls))
            return True

        return False


def _report_check_result(
    method_name: str,
    status: CheckStatus,
    expected_sig: Optional[inspect.Signature] = None,
    actual_sig: Optional[inspect.Signature] = None,
) -> None:
    """
    打印单个方法的协议实现检查结果。

    根据方法的检查状态（CheckStatus 枚举），输出不同风格的控制台信息：
    - ✅ 已实现；
    - ✅ 从默认实现注入；
    - ⚠️ 签名不一致；
    - ❌ 未实现也未注入。

    Args:
        method_name (str):
            被检查的方法名，通常为协议名派生后的形式（如 'greeter_greet'）。

        status (CheckStatus):
            方法的检查状态，枚举值包括：
            - OK：已正确实现；
            - INJECTED：从默认实现注入；
            - MISMATCH：方法签名不一致；
            - MISSING：方法不存在且无默认。

        expected_sig (Optional[inspect.Signature], optional):
            协议中定义的方法签名，仅在 MISMATCH 状态下使用。

        actual_sig (Optional[inspect.Signature], optional):
            实现类中的实际方法签名，仅在 MISMATCH 状态下使用。

    Returns:
        None
    """
    match status:
        case CheckStatus.OK:
            print(f"\t✅ {method_name}()")
        case CheckStatus.INJECTED:
            print(f"\t✅ {method_name}() → injected from defaults")
        case CheckStatus.MISMATCH:
            print(f"\t⚠️  {method_name}() → Signature mismatch!")
            print(f"\t\tExpected: {expected_sig}")
            print(f"\t\tFound:    {actual_sig}")
        case CheckStatus.MISSING:
            print(f"\t❌ {method_name}() → MISSING")
