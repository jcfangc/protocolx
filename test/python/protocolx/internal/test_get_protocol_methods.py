from src.python.definition.protocolx import Protocolx
from src.python.protocolx.internal import _get_protocol_methods


# 定义一个测试协议类
class MyProtocol(Protocolx):
    def method_1(self):
        pass  # 公开方法

    def method_2(self):
        pass  # 公开方法

    def _private_method(self):
        pass  # 私有方法

    def __init__(self):
        pass  # 魔术方法


def test_get_protocol_methods():
    # 获取协议类中的所有公开方法
    methods = _get_protocol_methods(MyProtocol)

    # 验证返回的类型是字典
    assert isinstance(methods, dict)

    # 验证返回的字典包含正确的方法
    assert "method_1" in methods
    assert "method_2" in methods

    # 验证私有方法不在字典中
    assert "_private_method" not in methods

    # 验证魔术方法不在字典中
    assert "__init__" not in methods

    # 验证字典的值是方法对象
    assert callable(methods["method_1"])
    assert callable(methods["method_2"])


def test_get_protocol_methods_empty_protocol():
    class EmptyProtocol(Protocolx):
        pass  # 没有定义任何方法

    methods = _get_protocol_methods(EmptyProtocol)

    # 验证返回的字典为空
    assert methods == {}


def test_get_protocol_methods_with_magic_methods():
    class MyProtocolWithMagicMethods(Protocolx):
        def method_1(self):
            pass

        def __init__(self):
            pass  # 魔术方法

    methods = _get_protocol_methods(MyProtocolWithMagicMethods)

    # 验证魔术方法不在字典中
    assert "__init__" not in methods
    assert "method_1" in methods


def test_get_protocol_methods_with_private_methods():
    class MyProtocolWithPrivateMethods(Protocolx):
        def method_1(self):
            pass

        def _private_method(self):
            pass  # 私有方法

    methods = _get_protocol_methods(MyProtocolWithPrivateMethods)

    # 验证私有方法不在字典中
    assert "_private_method" not in methods
    assert "method_1" in methods


def test_get_protocol_methods_multiple_methods():
    class MyProtocolWithMultipleMethods(Protocolx):
        def method_1(self):
            pass

        def method_2(self):
            pass

        def _private_method(self):
            pass

    methods = _get_protocol_methods(MyProtocolWithMultipleMethods)

    # 验证所有公开方法都被提取
    assert "method_1" in methods
    assert "method_2" in methods
    # 私有方法不在字典中
    assert "_private_method" not in methods
