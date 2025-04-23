from hypothesis import given
from hypothesis import strategies as st

from src.python.protocolx.internal import _inject_default_if_available


def test_inject_success() -> None:
    """
    测试 _inject_default_if_available 在 provider 中包含目标方法时的成功路径。

    当 Provider 类定义了与 method_name 相同的可调用方法时，
    函数应将此方法注入到 Target 类，并返回 True。

    Returns:
        None
    """

    class Target:
        pass

    class Provider:
        def greet(self):
            return "hi"

    result = _inject_default_if_available(Target, "greet", Provider)

    assert result is True
    assert hasattr(Target, "greet")
    assert Target().greet() == "hi"


def test_inject_blocked_by_existing_method() -> None:
    """
    测试 _inject_default_if_available 在目标类已存在同名方法时的行为。

    当目标类 `Target` 已经定义了与 `method_name` 相同的方法时，
    即使 `Provider` 中存在该方法，默认实现方法也不会被注入。
    函数应返回 False，且目标类的方法保持不变。

    Returns:
        None
    """

    class Target:
        def greet(self):
            return "original"

    class Provider:
        def greet(self):
            return "default"

    result = _inject_default_if_available(Target, "greet", Provider)

    assert result is False
    assert Target().greet() == "original"


def test_inject_method_not_found_in_provider() -> None:
    """
    测试 _inject_default_if_available 当 provider 中没有目标方法时的行为。

    当 `Provider` 中不包含与 `method_name` 相同的方法时，
    函数应返回 False，且目标类 `Target` 不会获得该方法的注入。

    Returns:
        None
    """

    class Target:
        pass

    class Provider:
        pass  # 不包含 greet 方法

    result = _inject_default_if_available(Target, "greet", Provider)

    assert result is False
    assert not hasattr(Target, "greet")


def test_inject_non_callable_in_provider() -> None:
    """
    测试 _inject_default_if_available 当 provider 中的方法不可调用时的行为。

    如果 `Provider` 中的方法不是可调用对象（例如是字符串或其他类型），
    函数应返回 False，且目标类 `Target` 不会获得该方法的注入。

    Returns:
        None
    """

    class Target:
        pass

    class Provider:
        greet = "not a function"

    result = _inject_default_if_available(Target, "greet", Provider)

    assert result is False
    assert not hasattr(Target, "greet")


def test_inject_with_none_provider() -> None:
    """
    测试 _inject_default_if_available 当 provider 为 None 时的行为。

    如果 `defaults_provider` 为 `None`，函数应返回 False，
    且目标类 `Target` 不会获得该方法的注入。

    Returns:
        None
    """

    class Target:
        pass

    result = _inject_default_if_available(Target, "greet", None)

    assert result is False
    assert not hasattr(Target, "greet")


@given(st.text(min_size=1, max_size=10))
def test_inject_with_random_method_name(name: str) -> None:
    """
    使用 Hypothesis 随机生成方法名，并测试 _inject_default_if_available 函数的行为。

    当 provider 中的动态方法名称与目标类目标方法名匹配时，
    如果能够成功注入方法，目标类应包含该方法，且该方法应返回预期结果。
    如果方法注入失败，确保目标类不包含该方法，或者该方法不可调用。

    Args:
        name (str): 随机生成的方法名，长度在 1 到 10 个字符之间。

    Returns:
        None
    """

    class Target:
        pass

    def generated_method(self):
        return "works"

    Provider = type("Provider", (), {name: generated_method})

    result = _inject_default_if_available(Target, name, Provider)

    if result:
        assert hasattr(Target, name)
        assert getattr(Target(), name)() == "works"
    else:
        # 方法未注入可能是因为名称冲突或异常名
        assert name not in vars(Target) or not callable(getattr(Target, name, None))
