import sys

from hypothesis import given
from hypothesis import strategies as st

from protocolx.global_var.protocol_cache import (
    del_protocol,
    get_protocol,
    set_protocol,
)


def test_set_and_get_protocol() -> None:
    """set 后可以 get，且返回同一对象"""
    sys.modules.pop("__anon_protocol__", None)

    class Dummy:
        pass

    set_protocol(name="_AnonProtocol_Test1", cls=Dummy)
    cls = get_protocol(name="_AnonProtocol_Test1")
    assert cls is Dummy
    # 未设置的名字返回 None
    assert get_protocol(name="_AnonProtocol_NotExist") is None


def test_set_and_del_protocol() -> None:
    """set 后可以 del，删除后无法 get"""
    sys.modules.pop("__anon_protocol__", None)

    class Dummy:
        pass

    set_protocol(name="_AnonProtocol_Test2", cls=Dummy)
    assert get_protocol(name="_AnonProtocol_Test2") is Dummy
    del_protocol(name="_AnonProtocol_Test2")
    assert get_protocol(name="_AnonProtocol_Test2") is None
    # 再删一次不报错
    del_protocol(name="_AnonProtocol_Test2")


@given(
    st.lists(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"),  # 大小写字母+数字
                whitelist_characters="_",
            ),
            min_size=1,
            max_size=8,
        ),
        min_size=1,
        max_size=5,
        unique=True,
    )
)
def test_protocol_set_get_del_hypothesis(names: list[str]) -> None:
    """Hypothesis: 随机批量 set/get/del 一致性"""
    sys.modules.pop("__anon_protocol__", None)
    # 随机插入
    for n in names:
        key = f"_AnonProtocol_{n}"
        cls = type(f"Cls_{n}", (), {})
        set_protocol(name=key, cls=cls)
    # 检查能 get 到
    for n in names:
        key = f"_AnonProtocol_{n}"
        out = get_protocol(name=key)
        assert out is not None and isinstance(out, type)
    # 随机删除
    for n in names:
        key = f"_AnonProtocol_{n}"
        del_protocol(name=key)
        assert get_protocol(name=key) is None


def test_del_protocol_on_nonexistent_key() -> None:
    """del_protocol 删除不存在的 key 不报错"""
    sys.modules.pop("__anon_protocol__", None)
    # 不存在时应无异常
    del_protocol(name="_AnonProtocol_NotExist")
