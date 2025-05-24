import sys

from hypothesis import given
from hypothesis import strategies as st

from protocolx.global_var.protocol_cache import (
    clear_protocol_cache,
    get_anon_protocol_module,
    get_protocol_cache,
    set_protocol,
)


def test_clear_only_anonprotocol_keys() -> None:
    """只清理 _AnonProtocol_ 前缀的 key，其他 key 保留"""
    sys.modules.pop("__anon_protocol__", None)
    # module = get_anon_protocol_module()

    class Dummy:
        pass

    set_protocol(name="_AnonProtocol_Foo", cls=Dummy)
    set_protocol(name="_AnonProtocol_Bar", cls=Dummy)
    set_protocol(name="Other", cls=Dummy)
    cache = get_protocol_cache()
    assert "_AnonProtocol_Foo" in cache
    assert "_AnonProtocol_Bar" in cache
    assert "Other" in cache
    clear_protocol_cache()
    cache = get_protocol_cache()
    assert "_AnonProtocol_Foo" not in cache
    assert "_AnonProtocol_Bar" not in cache
    assert "Other" in cache


def test_clear_protocol_cache_no_side_effect_on_magic() -> None:
    """不影响 __name__、__doc__ 等魔法属性"""
    sys.modules.pop("__anon_protocol__", None)
    module = get_anon_protocol_module()
    set_protocol(name="_AnonProtocol_Tmp", cls=type("Tmp", (), {}))
    clear_protocol_cache()
    cache = get_protocol_cache()
    # __name__ 等魔法属性依然存在
    assert "__name__" in cache
    assert module.__name__ == "__anon_protocol__"


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
    ),
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
    ),
)
def test_clear_protocol_cache_with_random_keys(
    anon_names: list[str], other_names: list[str]
) -> None:
    """
    hypothesis: 随机插入 _AnonProtocol_ 和非 _AnonProtocol_ 的 key，清理后只有非 anon 的留存
    """
    sys.modules.pop("__anon_protocol__", None)
    # 插入 _AnonProtocol_ 前缀的 key
    for n in anon_names:
        set_protocol(name=f"_AnonProtocol_{n}", cls=type(f"ClsA_{n}", (), {}))
    # 插入其它 key
    for n in other_names:
        set_protocol(name=f"Other_{n}", cls=type(f"ClsO_{n}", (), {}))
    clear_protocol_cache()
    cache = get_protocol_cache()
    # _AnonProtocol_ 前缀的都应该被删
    for n in anon_names:
        assert f"_AnonProtocol_{n}" not in cache
    # 其它 key 还应该存在
    for n in other_names:
        assert f"Other_{n}" in cache
    # 魔法属性保留
    assert "__name__" in cache
