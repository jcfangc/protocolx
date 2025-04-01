# test/test_internal/test_get_class_methods.py


from typing import Callable

from hypothesis import given
from hypothesis import strategies as st
from protocolx.internal import _get_class_methods


def make_class_with_methods(methods: dict[str, Callable]) -> type:
    """
    动态创建一个类，注入指定的可调用成员（方法、静态方法、类方法）
    """
    return type("DynamicClass", (), methods)


@given(
    # 方法名为非私有、合法的字符串
    method_names=st.lists(
        st.text(min_size=1).filter(str.isidentifier),
        min_size=1,
        max_size=5,
        unique=True,
    )
)
def test_get_class_methods_only_returns_directly_defined_callables(method_names):
    # 构造方法映射
    methods = {name: (lambda self=None: None) for name in method_names}
    cls = make_class_with_methods(methods)

    result = _get_class_methods(cls)

    assert isinstance(result, dict)
    assert set(result.keys()) == set(method_names)
    for name, fn in result.items():
        assert callable(fn)
