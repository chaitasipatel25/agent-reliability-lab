import re


def normalize_number(value: str) -> str:
    """Normalize formatted numbers such as 1,037 to 1037."""
    return value.replace(",", "").strip()



def answer_matches(response: str, expected: str) -> bool:
    """Match explicit numeric answers without guessing from arbitrary numbers."""
    try:
        expected_value = float(normalize_number(expected))
    except (ValueError, TypeError):
        return False

    text = normalize_number(response).strip()
    if not text:
        return False

    # Accept a response consisting only of a number.
    if re.fullmatch(r"-?\d+(?:\.\d+)?[.!]?", text):
        return float(text.rstrip(".!")) == expected_value

    # Extract explicitly presented answers in common model formats.
    patterns = [
        # Final Answer: 44 / Answer: 44
        r"(?im)^\s*(?:final\s+answer|answer)\s*[:=]\s*"
        r"(-?\d+(?:\.\d+)?)\s*[.!]?\s*$",

        # The answer is 1037 / Final answer is 1037
        r"(?i)\b(?:the\s+answer|final\s+answer)\s+is\s+"
        r"(-?\d+(?:\.\d+)?)\b",

        # LaTeX: \boxed{114}
        r"\\boxed\s*\{\s*(-?\d+(?:\.\d+)?)\s*\}",

        # Markdown: **72** at the end of a response
        r"\*\*(-?\d+(?:\.\d+)?)\*\*\s*[.!]?\s*$",
    ]

    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))

    if not matches:
        return False

    try:
        values = [float(value) for value in matches]
    except ValueError:
        return False

    # Reject contradictory answer candidates.
    if any(value != values[0] for value in values[1:]):
        return False

    return values[0] == expected_value



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
    error_type = trace.get("error_type")

    passed = answer_correct and tool_requirement_met and not error

    if passed:
        failure_category = None
    elif error_type == "step_limit_exceeded":
        failure_category = "step_limit_exceeded"
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
