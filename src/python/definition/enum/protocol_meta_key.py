from enum import Enum


class ProtocolMetaKey(Enum):
    """
    协议类内部用于声明元信息 (__protocolx__) 的字段键名。

    枚举值用于访问协议的元配置字典，如默认实现类、是否启用默认方法等。

    枚举值说明：
        - DEFAULTS: 指定默认方法的提供类；
        - USE_DEFAULT: 是否允许自动注入默认方法（bool）。
    """

    DEFAULTS = "defaults"
    USE_DEFAULT = "use_default"
