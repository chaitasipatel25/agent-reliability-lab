import json
from datetime import datetime, timezone
from pathlib import Path


TRACE_DIR = Path("traces")


def new_trace(task_id: str, model: str) -> dict:
    return {
        "task_id": task_id,
        "model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": None,
        "tool_calls": [],
        "final_response": "",
        "error": None,
        "passed": False,
    }


def save_trace(trace: dict) -> Path:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)

    path = TRACE_DIR / f"{trace['task_id']}.json"
    path.write_text(json.dumps(trace, indent=2))
    return path
