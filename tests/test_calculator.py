import pytest

from src.agent_reliability_lab.calculator import calculate


def test_arithmetic():
    assert calculate("(125 * 8) + 37") == "1037"


def test_division():
    assert calculate("144 / 12") == "12.0"


def test_rejects_unsupported_operation():
    with pytest.raises(ValueError):
        calculate("2 ** 10")


def test_rejects_function_calls():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('echo unsafe')")


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("1 / 0")
