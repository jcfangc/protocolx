import sys
from typing import MutableMapping

from hypothesis import given
from hypothesis import strategies as st

from protocolx.global_var.protocol_cache import (
    clear_protocol_cache,
    del_protocol,
    get_anon_protocol_module,
    get_protocol_cache,
    set_protocol,
)


def test_cache_is_mutable_mapping_and_dict_identity() -> None:
    """缓存类型是 MutableMapping[str, type] 并且与模块 __dict__ 同源"""
    sys.modules.pop("__anon_protocol__", None)
    module = get_anon_protocol_module()
    cache = get_protocol_cache()
    assert isinstance(cache, MutableMapping)
    assert cache is vars(module)
    # 模块 __dict__ 至少有 __name__ 属性
    assert "__name__" in cache


def test_cache_reflects_class_registration() -> None:
    """set_protocol 后缓存可查，del_protocol 后消失"""
    sys.modules.pop("__anon_protocol__", None)
    cache = get_protocol_cache()

    class Dummy:
        pass

    set_protocol(name="TestDummy", cls=Dummy)
    assert "TestDummy" in cache
    assert cache["TestDummy"] is Dummy
    del_protocol(name="TestDummy")
    assert "TestDummy" not in cache


def test_cache_cleared_with_clear_protocol_cache() -> None:
    """clear_protocol_cache 只清空 _AnonProtocol_ 前缀的 key，其他 key 保留"""
    sys.modules.pop("__anon_protocol__", None)

    class X:
        pass

    class Y:
        pass

    set_protocol(name="_AnonProtocol_Fake1", cls=X)
    set_protocol(name="_AnonProtocol_Fake2", cls=Y)
    set_protocol(name="NotAnon", cls=object)  # 非匿名协议类（不会被清空）

    cache = get_protocol_cache()
    assert (
        "_AnonProtocol_Fake1" in cache
        and "_AnonProtocol_Fake2" in cache
        and "NotAnon" in cache
    )
    clear_protocol_cache()
    cache = get_protocol_cache()
    assert "_AnonProtocol_Fake1" not in cache and "_AnonProtocol_Fake2" not in cache
    assert "NotAnon" in cache  # 非 _AnonProtocol_ 的保留
    assert "__name__" in cache


@given(
    st.lists(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"),  # 大小写字母+数字
                whitelist_characters="_",
            ),
            min_size=1,
            max_size=10,
        ),
        max_size=5,
        unique=True,
    )
)
def test_cache_random_insertion_and_deletion(names: list[str]) -> None:
    """Hypothesis: 随机插入/删除 _AnonProtocol_ key 后缓存反映一致"""
    sys.modules.pop("__anon_protocol__", None)
    for n in names:
        key = f"_AnonProtocol_{n}"
        cls = type(f"Cls_{n}", (), {})
        set_protocol(name=key, cls=cls)
    cache = get_protocol_cache()
    for n in names:
        key = f"_AnonProtocol_{n}"
        assert key in cache
        assert isinstance(cache[key], type)

        del_protocol(name=key)
        assert key not in get_protocol_cache()
