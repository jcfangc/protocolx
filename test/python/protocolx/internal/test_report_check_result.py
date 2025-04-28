import contextlib
import inspect
import io

from hypothesis import given
from hypothesis import strategies as st
from pytest import CaptureFixture

from src.python.definition.enum.check_status import CheckStatus  # 确保正确导入你的模块
from src.python.protocolx.internal import _report_check_result  # 确保路径正确


def test_report_check_result_ok(capsys: CaptureFixture):
    # 假设 CheckStatus.OK 状态
    _report_check_result("greeter_greet", CheckStatus.OK)

    captured = capsys.readouterr()  # 捕获输出
    assert "✅ greeter_greet()" in captured.out


def test_report_check_result_injected(capsys: CaptureFixture):
    # 假设 CheckStatus.INJECTED 状态
    _report_check_result("greeter_greet", CheckStatus.INJECTED)

    captured = capsys.readouterr()  # 捕获输出
    assert "✅ greeter_greet() → injected from defaults" in captured.out


def test_report_check_result_mismatch(capsys: CaptureFixture) -> None:
    expected_sig = inspect.signature(lambda x: x)
    actual_sig = inspect.signature(lambda x, y: x + y)

    _report_check_result(
        "greeter_greet", CheckStatus.MISMATCH, expected_sig, actual_sig
    )

    captured = capsys.readouterr()
    assert "greeter_greet() → Signature mismatch" in captured.out

    assert "Expected: (x)" in captured.out
    assert "Found:    (x, y)" in captured.out


def test_report_check_result_missing(capsys: CaptureFixture):
    # 假设 CheckStatus.MISSING 状态
    _report_check_result("greeter_greet", CheckStatus.MISSING)

    captured = capsys.readouterr()  # 捕获输出
    assert "❌ greeter_greet() → MISSING" in captured.out


# 3. 使用 hypothesis 进行进一步的签名测试
@given(method_name=st.text(min_size=1, max_size=10))
def test_report_check_result_with_random_method_names(method_name):
    expected_sig = inspect.signature(lambda x: x)
    actual_sig = inspect.signature(lambda x, y: x + y)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _report_check_result(
            method_name, CheckStatus.MISMATCH, expected_sig, actual_sig
        )

    out = buf.getvalue()
    assert f"⚠️  {method_name}() → Signature mismatch!" in out
    assert "Expected: (x)" in out
    assert "Found:    (x, y)" in out
