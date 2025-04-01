from enum import Enum


class CheckStatus(Enum):
    """
    协议方法检查状态。

    表示一个协议方法在实现类中对应的检查结果，常用于装饰器实现时的反馈。

    枚举值说明：
        - OK: 方法已正确实现，且签名一致。
        - INJECTED: 方法未在类中定义，但已从默认实现中注入。
        - MISMATCH: 方法已定义但签名与协议不一致。
        - MISSING: 方法未定义，且无可用默认实现。
    """

    OK = "ok"
    INJECTED = "injected"
    MISMATCH = "mismatch"
    MISSING = "missing"
