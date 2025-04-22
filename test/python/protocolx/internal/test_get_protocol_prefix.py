import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.python.protocolx.internal import _get_protocol_prefix


# 测试协议类名以 'I' 开头
def test_protocol_prefix_with_I():
    class IGreeter:
        pass

    prefix = _get_protocol_prefix(IGreeter)

    # 验证去掉首字母 'I' 并添加下划线
    assert prefix == "greeter_"


# 测试协议类名没有 'I' 开头
def test_protocol_prefix_without_I():
    class Greeter:
        pass

    prefix = _get_protocol_prefix(Greeter)

    # 如果类名没有 'I'，应该直接返回类名并加下划线
    assert prefix == "greeter_"


# 测试协议类名为单字母 I
def test_protocol_prefix_single_I():
    class I:
        pass

    prefix = _get_protocol_prefix(I)

    # 对于单字母 I，应返回 '_'
    assert prefix == "_"


# 测试协议类名为空
def test_protocol_prefix_empty():
    with pytest.raises(AttributeError):
        _get_protocol_prefix("")  # 空类名应引发异常


# 测试协议类名以 'I' 开头且包含大写字母
def test_protocol_prefix_with_mixed_case():
    class IMyCustomProtocol:
        pass

    prefix = _get_protocol_prefix(IMyCustomProtocol)

    # 去掉 'I' 并且小写其余部分，再加下划线
    assert prefix == "mycustomprotocol_"


# 测试多个协议类组合时前缀隔离
def test_protocol_prefix_with_multiple_protocols():
    class IProtocolOne:
        pass

    class IProtocolTwo:
        pass

    prefix_one = _get_protocol_prefix(IProtocolOne)
    prefix_two = _get_protocol_prefix(IProtocolTwo)

    # 验证每个协议类有独立的前缀，且不冲突
    assert prefix_one == "protocolone_"
    assert prefix_two == "protocoltwo_"
    assert prefix_one != prefix_two


# 使用 Hypothesis 测试协议类前缀生成
@given(
    st.text(
        min_size=1,
        alphabet=st.characters(whitelist_categories=["Ll", "Lu", "Lo", "Nl"]),
    )
)  # 只允许字母和符号
def test_protocol_prefix_with_hypothesis(class_name: str):
    if not class_name.startswith("I"):
        class_name = "I" + class_name  # 保证类名以 'I' 开头

    # 动态创建协议类
    CustomProtocol = type(class_name, (object,), {"__name__": class_name})

    # 获取前缀
    prefix = _get_protocol_prefix(CustomProtocol)

    # 验证去掉 'I' 后的小写前缀
    expected_prefix = class_name.lower().removeprefix("i") + "_"
    assert prefix == expected_prefix
