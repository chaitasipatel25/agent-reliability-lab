from types import SimpleNamespace

from src.agent_reliability_lab import runner


def make_response(content="", tool_calls=None):
    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls or [],
    )
    return SimpleNamespace(message=message)


def make_tool_call(name="calculate", arguments=None):
    function = SimpleNamespace(
        name=name,
        arguments=(
            {"expression": "6 * 7"}
            if arguments is None
            else arguments
        )
    )
    return SimpleNamespace(function=function)


def make_task():
    return {
        "id": "test-task",
        "prompt": "Calculate 6 times 7.",
        "expected_answer": "42",
        "require_tool": True,
    }


def disable_trace_saving(monkeypatch):
    monkeypatch.setattr(runner, "save_trace", lambda trace: None)


def test_runner_captures_final_response(monkeypatch):
    disable_trace_saving(monkeypatch)

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: make_response("The answer is 42."),
    )

    trace = runner.run_task(make_task())

    assert trace["final_response"] == "The answer is 42."
    assert trace["error"] is None
    assert trace["error_type"] is None


def test_runner_detects_step_limit(monkeypatch):
    disable_trace_saving(monkeypatch)
    monkeypatch.setattr(runner, "MAX_STEPS", 2)

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: make_response(
            tool_calls=[make_tool_call()]
        ),
    )

    trace = runner.run_task(make_task())

    assert len(trace["tool_calls"]) == 2
    assert trace["error"] == "Maximum agent steps reached"
    assert trace["error_type"] == "step_limit_exceeded"


def test_runner_records_unknown_tool(monkeypatch):
    disable_trace_saving(monkeypatch)

    responses = iter([
        make_response(
            tool_calls=[make_tool_call(name="unknown_tool")]
        ),
        make_response("The answer is 42."),
    ])

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: next(responses),
    )

    trace = runner.run_task(make_task())

    assert trace["error"] is None
    assert trace["tool_calls"][0]["tool"] == "unknown_tool"
    assert trace["tool_calls"][0]["error"] == "Unknown tool: unknown_tool"


def test_runner_records_calculator_exception(monkeypatch):
    disable_trace_saving(monkeypatch)

    def failing_calculator(expression):
        raise ValueError("Invalid arithmetic expression")

    monkeypatch.setattr(runner, "calculate", failing_calculator)

    responses = iter([
        make_response(
            tool_calls=[make_tool_call()]
        ),
        make_response("I could not calculate the answer."),
    ])

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: next(responses),
    )

    trace = runner.run_task(make_task())

    assert trace["error"] is None
    assert trace["tool_calls"][0]["error"] == "Invalid arithmetic expression"
    assert "Tool error:" in trace["tool_calls"][0]["result"]

def test_runner_records_missing_calculator_argument(monkeypatch):
    disable_trace_saving(monkeypatch)

    responses = iter([
        make_response(
            tool_calls=[make_tool_call(arguments={})]
        ),
        make_response("I could not calculate the answer."),
    ])

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: next(responses),
    )

    trace = runner.run_task(make_task())

    assert len(trace["tool_calls"]) == 1
    assert trace["tool_calls"][0]["error"] is not None
    assert "expression" in trace["tool_calls"][0]["error"]
    assert trace["error"] is None


def test_runner_recovers_after_tool_failure(monkeypatch):
    disable_trace_saving(monkeypatch)

    responses = iter([
        make_response(
            tool_calls=[make_tool_call(arguments={})]
        ),
        make_response(
            tool_calls=[make_tool_call()]
        ),
        make_response("The answer is 42."),
    ])

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: next(responses),
    )

    trace = runner.run_task(make_task())

    assert len(trace["tool_calls"]) == 2
    assert trace["tool_calls"][0]["error"] is not None
    assert trace["tool_calls"][1]["error"] is None
    assert trace["final_response"] == "The answer is 42."
    assert trace["error"] is None


def test_runner_records_multiple_tool_calls(monkeypatch):
    disable_trace_saving(monkeypatch)

    responses = iter([
        make_response(
            tool_calls=[
                make_tool_call(),
                make_tool_call(
                    arguments={"expression": "7 * 6"}
                ),
            ]
        ),
        make_response("The answer is 42."),
    ])

    monkeypatch.setattr(
        runner,
        "chat",
        lambda **kwargs: next(responses),
    )

    trace = runner.run_task(make_task())

    assert len(trace["tool_calls"]) == 2
    assert all(
        call["error"] is None
        for call in trace["tool_calls"]
    )