import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.python.protocolx.internal import _get_class_methods


# 定义测试用的类
class BaseClass:
    def inherited_method(self):
        pass


class TestClass(BaseClass):
    def instance_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    non_method = 42  # 非方法成员


class EmptyClass:
    pass


class NoMethodsClass:
    no_method = "I am not callable"


# 测试函数：验证返回类型和结构
def test_get_class_methods_structure():
    methods = _get_class_methods(TestClass)

    # 检查返回的是字典
    assert isinstance(methods, dict)
    # 键是字符串类型
    assert all(isinstance(name, str) for name in methods.keys())
    # 值是可调用对象（Callable）
    assert all(callable(member) for member in methods.values())


# 测试函数：验证返回值只包含类定义的可调用成员
def test_get_class_methods_no_inherited():
    methods = _get_class_methods(TestClass)
    # 确保继承的成员（如 `inherited_method`）没有被包含
    assert "inherited_method" not in methods


# 测试函数：确保静态方法、类方法和实例方法都被正确提取
def test_get_class_methods_types():
    methods = _get_class_methods(TestClass)

    # 检查静态方法
    assert "static_method" in methods
    assert methods["static_method"] == TestClass.static_method

    # 检查类方法
    assert "class_method" in methods
    assert methods["class_method"] == TestClass.class_method.__func__

    # 检查实例方法
    assert "instance_method" in methods

    assert methods["instance_method"] == TestClass.instance_method


# 测试函数：验证空类的情况
def test_get_class_methods_empty_class():
    methods = _get_class_methods(EmptyClass)
    # 确保返回一个空字典
    assert methods == {}


# 测试函数：验证类没有可调用成员的情况
def test_get_class_methods_no_callable_members():
    methods = _get_class_methods(NoMethodsClass)
    # 确保返回一个空字典
    assert methods == {}


# 使用 Hypothesis 测试：随机生成类，验证字典返回值结构
@given(st.builds(TestClass))
def test_get_class_methods_with_hypothesis(test_class_instance):
    methods = _get_class_methods(type(test_class_instance))
    assert isinstance(methods, dict)
    assert all(isinstance(name, str) for name in methods.keys())
    assert all(callable(member) for member in methods.values())


# Pytest 配合 Hypothesis 测试类的生成
@pytest.mark.parametrize("cls", [TestClass, EmptyClass, NoMethodsClass])
def test_get_class_methods_various_classes(cls):
    methods = _get_class_methods(cls)
    assert isinstance(methods, dict)
    assert all(isinstance(name, str) for name in methods.keys())
    assert all(callable(member) for member in methods.values()) if methods else True
