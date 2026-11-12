import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
TRACE_DIR = ROOT / "traces"
RUNS = 3


def main():
    REPORT_DIR.mkdir(exist_ok=True)
    TRACE_DIR.mkdir(exist_ok=True)

    history = []

    for run_number in range(1, RUNS + 1):
        print(f"\n{'=' * 12} Run {run_number}/{RUNS} {'=' * 12}")

        result = subprocess.run(
            [sys.executable, "scripts/run_eval.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        print(result.stdout)

        if result.returncode != 0:
            print(result.stderr)
            raise SystemExit(result.returncode)

        report = json.loads(
            (REPORT_DIR / "latest.json").read_text()
        )

        # Preserve each run rather than overwriting the previous report.
        run_path = REPORT_DIR / f"run_{run_number}.json"
        run_path.write_text(json.dumps(report, indent=2))

        # Preserve raw traces for this run.
        run_trace_dir = TRACE_DIR / f"run_{run_number}"
        run_trace_dir.mkdir(parents=True, exist_ok=True)

        for task in report["results"]:
            task_id = task["task_id"]
            source = TRACE_DIR / f"{task_id}.json"
            destination = run_trace_dir / f"{task_id}.json"

            if not source.exists():
                raise FileNotFoundError(
                    f"Missing trace for task {task_id}: {source}"
                )

            destination.write_text(source.read_text())

        history.append({
            "run": run_number,
            "pass_rate": report["pass_rate"],
            "passed": report["passed"],
            "total_tasks": report["total_tasks"],
            "mean_duration_ms": report["mean_duration_ms"],
            "failure_categories": report["failure_categories"],
            "total_tool_calls": report["total_tool_calls"],
            "total_tool_failures": report["total_tool_failures"],
            "tool_success_rate": report["tool_success_rate"],
            "recovered_tasks": report["recovered_tasks"],
        })

    pass_rates = [item["pass_rate"] for item in history]
    latencies = [
        item["mean_duration_ms"]
        for item in history
        if item["mean_duration_ms"] is not None
    ]

    summary = {
        "model": "qwen3:8b",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runs": RUNS,
        "mean_pass_rate": round(statistics.mean(pass_rates), 4),
        "pass_rate_by_run": pass_rates,
        "mean_run_latency_ms": (
            round(statistics.mean(latencies), 2)
            if latencies else None
        ),
        "run_results": history,
        "mean_tool_success_rate": (
            round(
                statistics.mean(
                    item["tool_success_rate"] for item in history
                ),
                4,
            )
            if history else 0
        ),
        "total_tool_calls": sum(
            item["total_tool_calls"] for item in history
        ),
        "total_tool_failures": sum(
            item["total_tool_failures"] for item in history
        ),
        "total_recovered_tasks": sum(
            item["recovered_tasks"] for item in history
        ),
    }

    summary_path = REPORT_DIR / "repeated_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    print("\n=== Repeated Evaluation Summary ===")
    print(f"Runs: {RUNS}")
    print(f"Pass rate per run: {pass_rates}")
    print(f"Mean pass rate: {summary['mean_pass_rate']:.0%}")
    print(f"Mean run latency: {summary['mean_run_latency_ms']} ms")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
