import re


def normalize_number(value: str) -> str:
    """Normalize numbers such as 1,037 and 1037."""
    return value.replace(",", "").strip()


def answer_matches(response: str, expected: str) -> bool:
    """Compare the expected number with the last numeric value in a response."""
    import re

    def normalize(value: str) -> str:
        return value.replace(",", "").strip()

    # Match integers, decimals, signed numbers, and comma-formatted numbers.
    pattern = r"(?<![\w.])-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    numbers = re.findall(pattern, response)

    if not numbers:
        return False

    actual = normalize(numbers[-1])
    expected = normalize(str(expected))

    try:
        return float(actual) == float(expected)
    except ValueError:
        return False


def evaluate_task(trace: dict) -> dict:
    """Score a task trace and classify failures."""
    response = trace.get("final_response", "")
    expected = str(trace.get("expected_answer", ""))

    answer_correct = answer_matches(response, expected)

    tool_calls = trace.get("tool_calls", [])
    calculator_used = any(
        call.get("tool") == "calculate"
        for call in tool_calls
    )

    tool_requirement_met = (
        calculator_used
        if trace.get("tool_required", False)
        else True
    )

    error = trace.get("error")
    passed = answer_correct and tool_requirement_met and not error

    if passed:
        failure_category = None
    elif error:
        failure_category = "execution_error"
    elif not tool_requirement_met:
        failure_category = "tool_use_failure"
    elif not answer_correct:
        failure_category = "incorrect_answer"
    else:
        failure_category = "unknown_failure"

    return {
        "task_id": trace.get("task_id"),
        "passed": passed,
        "expected_answer": expected,
        "answer_correct": answer_correct,
        "tool_required": trace.get("tool_required", False),
        "calculator_used": calculator_used,
        "failure_category": failure_category,
        "duration_ms": trace.get("duration_ms"),
        "error": error,
    }
