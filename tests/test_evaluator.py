
from src.agent_reliability_lab.evaluator import (
    answer_matches,
    evaluate_task,
)


def test_answer_matches_integer():
    assert answer_matches("The answer is 1037.", "1037")


def test_answer_matches_formatted_number():
    assert answer_matches("The answer is 1,037.", "1037")


def test_does_not_match_partial_number():
    assert not answer_matches("The answer is 10370.", "1037")


def test_evaluate_successful_trace():
    trace = {
        "task_id": "math-001",
        "final_response": "The answer is 1037.",
        "expected_answer": "1037",
        "tool_required": True,
        "tool_calls": [{"tool": "calculate"}],
        "error": None,
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is True
    assert result["failure_category"] is None


def test_evaluate_missing_tool():
    trace = {
        "task_id": "math-002",
        "final_response": "The answer is 12.",
        "expected_answer": "12",
        "tool_required": True,
        "tool_calls": [],
        "error": None,
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "tool_use_failure"


def test_rejects_wrong_final_answer():
    assert not answer_matches(
        "The expected answer is 1037, but my final answer is 10370.",
        "1037",
    )


def test_rejects_wrong_sign():
    assert not answer_matches("The answer is -12.", "12")


def test_rejects_response_without_numbers():
    assert not answer_matches("I could not calculate the answer.", "1037")


def test_evaluate_incorrect_answer():
    trace = {
        "task_id": "math-wrong",
        "final_response": "The answer is 999.",
        "expected_answer": "1037",
        "tool_required": True,
        "tool_calls": [{"tool": "calculate"}],
        "error": None,
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "incorrect_answer"


def test_evaluate_execution_error():
    trace = {
        "task_id": "math-error",
        "final_response": "",
        "expected_answer": "1037",
        "tool_required": True,
        "tool_calls": [],
        "error": "Model unavailable",
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "execution_error"
