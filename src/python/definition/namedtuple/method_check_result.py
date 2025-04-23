from typing import NamedTuple


class MethodCheckResult(NamedTuple):
    """
    方法检查结果

    Attrs:
        - exists : bool
            目标类是否定义了该方法。
        - signature_ok : bool
            若方法存在，签名是否与协议定义一致。
    """

    exists: bool
    signature_ok: bool
