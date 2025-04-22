from typing import Any, Dict, Protocol

from definition.enum.protocol_meta_key import ProtocolMetaKey


class Protocolx(Protocol):
    """
    所有自定义协议（Protocol）应继承自该基类，以支持结构化协议检查系统。

    协议实现类可通过 __protocolx__ 属性声明协议元信息，如：

        - DEFAULTS: 提供默认方法的类；
        - USE_DEFAULT: 是否允许使用默认实现。

    系统将通过该元信息指导 `@implements(...)` 装饰器行为。
    """

    __protocolx__: Dict[ProtocolMetaKey, Any]
    """
    协议元信息配置字典，用于指导协议实现检查系统。
    """
