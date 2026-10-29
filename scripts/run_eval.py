
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent_reliability_lab.evaluator import evaluate_task
from src.agent_reliability_lab.runner import run_task

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "smoke.jsonl"
REPORT_DIR = ROOT / "reports"
TRACE_DIR = ROOT / "traces"


def main():
    tasks = [
        json.loads(line)
        for line in DATASET.read_text().splitlines()
        if line.strip()
    ]

    results = []

    for task in tasks:
        print(f"\nRunning task: {task['id']}")

        trace = run_task(task)
        result = evaluate_task(trace)
        results.append(result)

        print(f"Passed: {result['passed']}")
        print(f"Answer correct: {result['answer_correct']}")
        print(f"Calculator used: {result['calculator_used']}")
        print(f"Duration: {result['duration_ms']} ms")

        if result["failure_category"]:
            print(f"Failure: {result['failure_category']}")

    total = len(results)
    passed = sum(result["passed"] for result in results)
    durations = [
        result["duration_ms"]
        for result in results
        if result["duration_ms"] is not None
    ]

    failure_counts = {}
    for result in results:
        category = result["failure_category"]
        if category:
            failure_counts[category] = failure_counts.get(category, 0) + 1

    report = {
        "model": "qwen3:8b",
        "total_tasks": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 4) if total else 0,
        "mean_duration_ms": (
            round(statistics.mean(durations), 2) if durations else None
        ),
        "failure_categories": failure_counts,
        "results": results,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "latest.json"
    report_path.write_text(json.dumps(report, indent=2))

    print("\n=== Benchmark Summary ===")
    print(f"Pass rate: {passed}/{total} ({report['pass_rate']:.0%})")
    print(f"Mean duration: {report['mean_duration_ms']} ms")
    print(f"Failure categories: {failure_counts}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
