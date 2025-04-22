from typing import Type

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.python.definition.protocolx import ProtocolMeta, Protocolx
from src.python.protocolx.internal import _get_protocol_meta  # 按实际路径修改


def test_get_protocol_meta_with_explicit_meta() -> None:
    """协议类显式提供 __protocolx__"""

    class DefaultImpl:
        def hello(self) -> str:
            return "hi"

    class IMyProto(Protocolx):
        __protocolx__ = ProtocolMeta(DEFAULT=DefaultImpl, USE_DEFAULT=False)

    meta = _get_protocol_meta(IMyProto)

    assert isinstance(meta, ProtocolMeta)
    assert meta.DEFAULT is DefaultImpl
    assert meta.USE_DEFAULT is False


def test_get_protocol_meta_with_empty_meta() -> None:
    """协议类提供空 ProtocolMeta()，验证默认字段"""

    class IEmptyMetaProto(Protocolx):
        __protocolx__ = ProtocolMeta()  # DEFAULT=None, USE_DEFAULT=True

    meta = _get_protocol_meta(IEmptyMetaProto)

    assert isinstance(meta, ProtocolMeta)
    assert meta.DEFAULT is None
    assert meta.USE_DEFAULT is True


def test_get_protocol_meta_missing_attr() -> None:
    """协议类未声明 __protocolx__ —— 按当前实现应触发 AttributeError"""

    class INoMetaProto(Protocolx):
        pass

    with pytest.raises(AttributeError):
        _get_protocol_meta(INoMetaProto)


@given(
    use_default=st.booleans(),
    class_name=st.text(
        min_size=1,
        max_size=10,
        alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
    ),
)
def test_get_protocol_meta_random(use_default: bool, class_name: str) -> None:
    """
    随机生成：
      * 一个默认实现类 (名字随机)
      * USE_DEFAULT 布尔值
    确认 _get_protocol_meta 能如实返回 ProtocolMeta
    """
    # 动态创建默认实现类
    DefaultImpl: Type = type(f"{class_name}Impl", (), {})

    # 动态创建协议类
    class IRandomProto(Protocolx):
        __protocolx__ = ProtocolMeta(DEFAULT=DefaultImpl, USE_DEFAULT=use_default)

    meta = _get_protocol_meta(IRandomProto)

    assert isinstance(meta, ProtocolMeta)
    assert meta.DEFAULT is DefaultImpl
    assert meta.USE_DEFAULT is use_default
