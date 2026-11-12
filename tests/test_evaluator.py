
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

def test_does_not_accept_expected_answer_mentioned_as_context():
    response = (
        "I calculated 999, but the expected answer is 1037."
    )
    assert not answer_matches(response, "1037")

    

def test_rejects_expected_answer_used_as_context():
    assert not answer_matches(
        "I calculated 999, but the expected answer is 1037.",
        "1037",
    )


def test_rejects_conflicting_answer_labels():
    assert not answer_matches(
        "The answer is 999. The final answer is 1037.",
        "1037",
    )


def test_rejects_unlabeled_explanation_ending_in_expected_number():
    assert not answer_matches(
        "I considered 12, 15, and 18, but could not determine the answer.",
        "18",
    )


def test_accepts_standalone_numeric_response():
    assert answer_matches("1037", "1037")


def test_accepts_negative_standalone_numeric_response():
    assert answer_matches("-12", "-12")


def test_rejects_malformed_expected_answer():
    assert not answer_matches("The answer is 12.", "not-a-number")


def test_rejects_expected_answer_used_as_context():
    assert not answer_matches(
        "I calculated 999, but the expected answer is 1037.",
        "1037",
    )


def test_rejects_conflicting_answer_labels():
    assert not answer_matches(
        "The answer is 999. The final answer is 1037.",
        "1037",
    )


def test_rejects_unlabeled_explanation_ending_in_expected_number():
    assert not answer_matches(
        "I considered 12, 15, and 18, but could not determine the answer.",
        "18",
    )


def test_accepts_standalone_numeric_response():
    assert answer_matches("1037", "1037")


def test_accepts_negative_standalone_numeric_response():
    assert answer_matches("-12", "-12")


def test_rejects_malformed_expected_answer():
    assert not answer_matches("The answer is 12.", "not-a-number")


def test_accepts_latex_boxed_answer():
    assert answer_matches(
        r"The result is $\boxed{114}$.",
        "114",
    )


def test_accepts_latex_display_math_answer():
    assert answer_matches(
        "The result is:\n\n$$\n\\boxed{12}\n$$",
        "12",
    )


def test_accepts_markdown_bold_answer():
    assert answer_matches(
        "The result of (42 - 18) * 3 is **72**.",
        "72",
    )


def test_accepts_labeled_answer_with_explanation():
    assert answer_matches(
        "The result is 44.\n\nFinal Answer: 44",
        "44",
    )


def test_rejects_conflicting_boxed_answers():
    assert not answer_matches(
        r"The answer is $\boxed{999}$, "
        r"but the final result is $\boxed{1037}$.",
        "1037",
    )

def test_evaluate_step_limit_exceeded():
    trace = {
        "task_id": "math-loop",
        "final_response": "",
        "expected_answer": "12",
        "tool_required": True,
        "tool_calls": [{"tool": "calculate"}],
        "error": "Maximum agent steps reached",
        "error_type": "step_limit_exceeded",
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "step_limit_exceeded"


def test_evaluate_execution_error():
    trace = {
        "task_id": "math-crash",
        "final_response": "",
        "expected_answer": "12",
        "tool_required": True,
        "tool_calls": [],
        "error": "Connection refused",
        "error_type": "execution_error",
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "execution_error"

def test_legacy_trace_without_error_type():
    trace = {
        "task_id": "legacy-error",
        "final_response": "",
        "expected_answer": "12",
        "tool_required": True,
        "tool_calls": [],
        "error": "Model unavailable",
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["failure_category"] == "execution_error"

def test_evaluate_calculator_execution_failure():
    trace = {
        "task_id": "math-tool-error",
        "final_response": "I could not calculate the answer.",
        "expected_answer": "42",
        "tool_required": True,
        "tool_calls": [
            {
                "tool": "calculate",
                "result": "Tool error: Invalid expression",
                "error": "Invalid expression",
            }
        ],
        "error": None,
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["calculator_used"] is True
    assert result["calculator_succeeded"] is False
    assert result["failure_category"] == "tool_execution_failure"
    assert result["tool_call_count"] == 1
    assert result["tool_failure_count"] == 1
    assert result["tool_success_count"] == 0
    assert result["recovered_from_tool_failure"] is False


def test_evaluate_successful_tool_retry():
    trace = {
        "task_id": "math-tool-retry",
        "final_response": "The answer is 42.",
        "expected_answer": "42",
        "tool_required": True,
        "tool_calls": [
            {
                "tool": "calculate",
                "result": "Tool error: Temporary failure",
                "error": "Temporary failure",
            },
            {
                "tool": "calculate",
                "result": "42",
                "error": None,
            },
        ],
        "error": None,
        "duration_ms": 1500,
    }

    result = evaluate_task(trace)

    assert result["passed"] is True
    assert result["calculator_used"] is True
    assert result["calculator_succeeded"] is True
    assert result["failure_category"] is None
    assert result["tool_call_count"] == 2
    assert result["tool_failure_count"] == 1
    assert result["tool_success_count"] == 1
    assert result["recovered_from_tool_failure"] is True


def test_evaluate_wrong_answer_after_successful_tool_call():
    trace = {
        "task_id": "math-wrong-after-tool",
        "final_response": "The answer is 41.",
        "expected_answer": "42",
        "tool_required": True,
        "tool_calls": [
            {
                "tool": "calculate",
                "result": "42",
                "error": None,
            }
        ],
        "error": None,
        "duration_ms": 1000,
    }

    result = evaluate_task(trace)

    assert result["passed"] is False
    assert result["calculator_succeeded"] is True
    assert result["failure_category"] == "incorrect_answer"

def test_accepts_bold_final_answer_with_latex_math():
    response = (
        "The calculation is shown above.\n\n"
        "**Final Answer**: $1037$"
    )
    assert answer_matches(response, "1037")


def test_accepts_final_answer_with_latex_math():
    assert answer_matches(
        "Final Answer: $1037$",
        "1037",
    )


def test_accepts_bold_answer_label():
    assert answer_matches(
        "**Answer**: 1037",
        "1037",
    )


def test_rejects_conflicting_bold_final_answer():
    response = (
        "The answer is 999.\n"
        "**Final Answer**: $1037$"
    )
    assert not answer_matches(response, "1037")