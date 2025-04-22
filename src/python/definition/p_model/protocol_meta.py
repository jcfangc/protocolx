from typing import Any, Optional, Type

from pydantic import BaseModel


class ProtocolMeta(BaseModel):
    """
    协议元信息模型，用于存储协议的元数据。

    - `DEFAULTS`: 提供默认方法的类；
    - `USE_DEFAULT`: 是否允许使用默认实现。
    """

    DEFAULT: Optional[Type[Any]] = None  # 默认实现类，类型为类对象（可选）
    USE_DEFAULT: bool = True  # 是否使用默认实现，默认为 True
