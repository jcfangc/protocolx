import sys
import types

import pytest
from hypothesis import given
from hypothesis import strategies as st

from protocolx.global_var.protocol_cache import get_anon_protocol_module


def test_module_created_and_returned() -> None:
    """第一次调用应创建模块，后续调用返回同一对象"""
    # 保证环境干净
    sys.modules.pop("__anon_protocol__", None)
    module = get_anon_protocol_module()
    assert isinstance(module, types.ModuleType)
    assert module is sys.modules["__anon_protocol__"]
    # 再次调用返回同一个对象
    module2 = get_anon_protocol_module()
    assert module2 is module


def test_module_only_created_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """反复调用不应新建对象"""
    sys.modules.pop("__anon_protocol__", None)
    # 记录 type 调用次数
    created = []
    orig_module_type = types.ModuleType

    def fake_module_type(name):
        created.append(name)
        return orig_module_type(name)

    monkeypatch.setattr(types, "ModuleType", fake_module_type)
    m1 = get_anon_protocol_module()
    m2 = get_anon_protocol_module()
    assert m1 is m2
    # 只创建了一次
    assert created.count("__anon_protocol__") == 1


@given(st.booleans())
def test_delete_and_recreate_module(delete_first: bool) -> None:
    """
    随机测试：删掉模块再调用应重新创建
    """
    sys.modules.pop("__anon_protocol__", None)
    m1 = get_anon_protocol_module()
    assert "__anon_protocol__" in sys.modules
    if delete_first:
        sys.modules.pop("__anon_protocol__")
        assert "__anon_protocol__" not in sys.modules
    m2 = get_anon_protocol_module()
    assert "__anon_protocol__" in sys.modules
    assert isinstance(m2, types.ModuleType)
    # 新旧 module 不是同一个对象（如果删过）
    if delete_first:
        assert m1 is not m2
    else:
        assert m1 is m2


def test_module_has_expected_name() -> None:
    """模块名称正确"""
    sys.modules.pop("__anon_protocol__", None)
    module = get_anon_protocol_module()
    assert module.__name__ == "__anon_protocol__"
