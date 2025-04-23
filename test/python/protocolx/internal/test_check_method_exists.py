# test_check_method_exists.py
import inspect
from types import FunctionType
from typing import Callable, Dict

from hypothesis import given
from hypothesis import strategies as st

from src.python.definition.namedtuple.method_check_result import MethodCheckResult
from src.python.protocolx.internal import _check_method_exists


def help_make_func_with_n_positional_args(n: int) -> Callable[..., None]:
    """
    动态生成一个只含 n 个位置参数的简单函数

    Args:
        n (int): 位置参数的数量

    Returns:
        Callable[..., None]: 一个函数对象，接受 n 个位置参数
    """
    # 生成形参列表字符串  e.g.  "p0, p1, p2"
    arg_list: str = ", ".join(f"p{i}" for i in range(n))

    # 构造函数源码
    # 注意换行与缩进，以便 exec 正常解析
    src: str = f"def _tmp({arg_list}):\n    pass"

    # 在独立命名空间执行源码，防止污染全局
    ns: Dict[str, FunctionType] = {}
    exec(src, ns)

    # 返回动态生成的函数对象
    return ns["_tmp"]


def test_method_missing() -> None:
    """方法不存在：返回 (False, False)"""

    def proto(x):  # 协议签名
        pass

    result = _check_method_exists(
        expected_name="foo",
        proto_method=proto,
        cls_methods={},  # 实现类没有任何方法
    )
    assert result == MethodCheckResult(exists=False, signature_ok=False)


def test_method_exists_and_signature_ok() -> None:
    """方法存在且签名一致：返回 (True, True)"""

    def proto(a, b):  # 协议签名
        pass

    # 实现函数复用同一签名
    impl = proto

    result = _check_method_exists(
        expected_name="bar",
        proto_method=proto,
        cls_methods={"bar": impl},
    )
    assert result == MethodCheckResult(exists=True, signature_ok=True)


def test_method_exists_but_signature_mismatch() -> None:
    """方法存在但签名不一致：返回 (True, False)"""

    def proto(x):  # 协议签名
        pass

    def impl(x, y):  # 多一个参数
        pass

    result = _check_method_exists(
        expected_name="baz",
        proto_method=proto,
        cls_methods={"baz": impl},
    )
    assert result == MethodCheckResult(exists=True, signature_ok=False)


@given(
    n_proto=st.integers(min_value=0, max_value=3),
    n_impl=st.integers(min_value=-3, max_value=3),
    name=st.text(min_size=1, max_size=10),
)
def test_random_signatures(n_proto: int, n_impl: int, name: str) -> None:
    """
    随机生成不同参数数量的协议/实现函数，验证结果分类：
      * 方法缺失
      * 签名一致
      * 签名不一致

    Args:
        n_proto (int): 协议函数的参数数量
        n_impl (int): 实现函数的参数数量
        name (str): 实现类中期望的方法名
    """
    proto_method = help_make_func_with_n_positional_args(n_proto)

    # 50% 概率让实现缺失
    if n_impl < 0:
        cls_methods = {}  # 不存在
        result = _check_method_exists(name, proto_method, cls_methods)
        assert result == MethodCheckResult(exists=False, signature_ok=False)
    else:
        impl_method = help_make_func_with_n_positional_args(n_impl)
        cls_methods = {name: impl_method}
        result = _check_method_exists(name, proto_method, cls_methods)

        assert result.exists is True
        expect_match = inspect.signature(proto_method) == inspect.signature(impl_method)
        assert result.signature_ok is expect_match
