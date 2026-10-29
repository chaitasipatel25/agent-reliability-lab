
import time

from ollama import chat

from src.agent_reliability_lab.calculator import calculate
from src.agent_reliability_lab.tracing import new_trace, save_trace

MODEL = "qwen3:8b"
MAX_STEPS = 5


def run_task(task: dict, model: str = MODEL) -> dict:
    """Run one benchmark task and save a trace of the execution."""
    trace = new_trace(task["id"], model)
    started = time.perf_counter()

    messages = [
        {
            "role": "user",
            "content": task["prompt"],
        }
    ]

    try:
        for step in range(MAX_STEPS):
            response = chat(
                model=model,
                messages=messages,
                tools=[calculate],
            )

            messages.append(response.message)
            tool_calls = response.message.tool_calls or []

            if not tool_calls:
                trace["final_response"] = response.message.content or ""
                break

            for call in tool_calls:
                tool_name = call.function.name
                arguments = call.function.arguments or {}
                tool_started = time.perf_counter()

                if tool_name == "calculate":
                    try:
                        result = calculate(arguments["expression"])
                        error = None
                    except Exception as exc:
                        result = f"Tool error: {exc}"
                        error = str(exc)
                else:
                    result = f"Unknown tool: {tool_name}"
                    error = result

                trace["tool_calls"].append(
                    {
                        "step": step + 1,
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": str(result),
                        "error": error,
                        "duration_ms": round(
                            (time.perf_counter() - tool_started) * 1000, 2
                        ),
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": str(result),
                    }
                )
        else:
            trace["error"] = "Maximum agent steps reached"

    except Exception as exc:
        trace["error"] = f"{type(exc).__name__}: {exc}"

    trace["duration_ms"] = round(
        (time.perf_counter() - started) * 1000, 2
    )
    trace["tool_required"] = task.get("require_tool", False)
    trace["expected_answer"] = task["expected_answer"]
    trace["passed"] = False  # The evaluator will determine this later.

    save_trace(trace)
    return trace

