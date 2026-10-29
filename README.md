# Agent Reliability Lab

**An evaluation and observability harness for tool-using AI agents.**

Agent Reliability Lab explores a practical question: how do we know whether an AI agent is actually reliable, rather than simply observing that it produced a plausible response?

The project starts with a locally running LLM, a deterministic calculator tool, and a repeatable evaluation harness. It captures execution traces, checks agent behavior against explicit criteria, categorizes failures, and generates reports that make regressions easier to detect.

This is an evolving engineering project focused on **evaluation, observability, and reliability** for AI agents.

> **Project status:** Early-stage prototype. The current benchmark is a small arithmetic smoke test, not evidence of general-purpose agent reliability.

## Why this project?

Tool-using agents introduce failure modes that ordinary unit tests don't fully capture:

- An agent can return a plausible answer without using a required tool.
- A tool call can fail, receive invalid arguments, or return an unexpected result.
- A model can produce an incorrect final answer despite successful tool execution.
- Changes to prompts, models, or agent logic can introduce regressions.
- A successful final response can hide inefficient or unnecessarily repeated tool calls.

This project aims to make those behaviors observable and measurable through repeatable experiments.

## Current capabilities

- **Local model execution:** Run an agent with Ollama and Qwen3, without requiring a hosted LLM API.
- **Tool execution:** Give the model access to a calculator tool with a restricted arithmetic evaluator.
- **Bounded agent loop:** Limit tool-execution iterations to prevent unbounded loops.
- **Execution tracing:** Capture tool calls, arguments, results, errors, timing, and the final response in JSON traces.
- **Independent evaluation:** Evaluate the final answer and whether required tool usage occurred.
- **Failure categorization:** Distinguish incorrect answers, tool-use failures, and execution errors.
- **Automated tests:** Test calculator behavior and evaluator edge cases.
- **Repeatable experiments:** Run the evaluation multiple times and summarize results.
- **Machine-readable reports:** Store evaluation results as JSON for later comparison and analysis.

## Architecture

```text
Benchmark dataset (JSONL)
          |
          v
      Eval runner
          |
          v
     Agent loop
          |
          v
   Local LLM (Ollama)
          |
          v
   Calculator tool
          |
          v
 Final response + trace
          |
          v
 Independent evaluator
          |
          v
 Results + failure categories
          |
          v
 JSON reports
```

The model is responsible for deciding how to respond and when to call the tool. The calculator performs the arithmetic, while the evaluator independently checks the observed outcome against the benchmark's requirements.

This separation is intentional: **the agent should not be the sole judge of its own success.**

## Technology stack

- Python
- Ollama
- Qwen3 8B
- pytest
- JSONL benchmark datasets
- JSON execution traces and evaluation reports
- GitHub Actions CI (planned or in progress, depending on the current repository state)

## Getting started

### Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/)
- Git

### 1. Install and start the local model

Install Ollama, then download the model:

```bash
ollama pull qwen3:8b
```

Confirm that the model is available:

```bash
ollama list
```

Make sure the Ollama service is running before launching evaluations.

### 2. Set up the Python environment

Clone the repository and enter its directory:

```bash
git clone <your-repository-url>
cd agent-reliability-lab
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install ollama pytest
```

### 3. Run the unit tests

```bash
python -m pytest -q
```

The unit tests cover deterministic calculator behavior and evaluator behavior, including incorrect answers and execution failures.

### 4. Run the evaluation

```bash
python scripts/run_eval.py
```

The runner loads the benchmark dataset, executes each task, evaluates the results, writes execution traces, and generates a summary report.

### 5. Run repeated evaluations

```bash
python scripts/run_repeated_eval.py
```

Repeated runs help expose variability that a single successful execution may hide.

> Model evaluations require a running Ollama service and can take significantly longer than the deterministic unit tests.

## Benchmark design

The initial benchmark lives in `datasets/smoke.jsonl`.

Each task defines a unique ID, a prompt, an expected answer, and whether calculator-tool usage is required.

Example:

```json
{
  "id": "math-001",
  "prompt": "Use the calculate tool to compute 125 * 8 + 37. Give the final answer clearly.",
  "expected_answer": "1037",
  "require_tool": true
}
```

The smoke dataset currently covers six arithmetic tasks. It provides a small, reproducible baseline for testing the agent loop and evaluation pipeline.

### Evaluation criteria

| Metric | What it measures |
|---|---|
| Answer correctness | Whether the final response matches the expected result |
| Tool-use compliance | Whether a required calculator tool was used |
| Execution errors | Whether an error occurred during execution |
| Pass rate | Percentage of tasks satisfying the evaluation criteria |
| Latency | Time spent executing a task |
| Failure category | The primary reason a task did not pass |

These metrics describe the tested tasks and configured model. They should not be interpreted as a universal measure of agent intelligence or reliability.

## Tracing and reports

The project separates execution evidence from evaluation results.

- `traces/` — per-task JSON execution traces.
- `reports/latest.json` — results from the latest evaluation.
- `reports/run_*.json` — reports from repeated runs.
- `reports/repeated_summary.json` — aggregate summary across repeated runs.

A trace records information such as the task ID, model, start time, duration, tool calls, final response, execution error, and pass status.

The evaluator determines the final outcome after execution. This allows the project to inspect what happened, not just whether the task passed.

Generated traces and reports are local artifacts and should be reviewed before committing them to version control.

## Repository structure

```text
agent-reliability-lab/
├── datasets/
│   └── smoke.jsonl
├── src/
│   └── agent_reliability_lab/
│       ├── calculator.py
│       ├── evaluator.py
│       ├── runner.py
│       └── tracing.py
├── tests/
│   ├── test_calculator.py
│   └── test_evaluator.py
├── scripts/
│   ├── run_eval.py
│   └── run_repeated_eval.py
├── traces/
├── reports/
├── .github/
│   └── workflows/
├── README.md
└── .gitignore
```

## Work in progress

The following items are planned improvements, not claims about functionality already completed.

- [ ] **Expand the benchmark:** Add multi-step tasks, malformed tool arguments, tool errors, missing tool calls, and tasks with misleading intermediate responses.
- [ ] **Strengthen evaluation:** Handle numeric formats and ambiguous final answers more robustly; test evaluator limitations explicitly.
- [ ] **Measure reliability over repeated runs:** Track pass-rate variation, latency distributions, and failure rates across runs.
- [ ] **Improve trace quality:** Add explicit step-level outcomes, consistent timestamps, and more structured error information.
- [ ] **Add regression testing:** Run deterministic tests automatically on pull requests and verify the CI workflow.
- [ ] **Compare models and configurations:** Evaluate different local models, prompts, and agent-loop settings using the same benchmark.
- [ ] **Add observability integration:** Explore OpenTelemetry and an agent-tracing UI such as Arize Phoenix.
- [ ] **Improve packaging and reproducibility:** Define project dependencies and configuration in a standard Python project setup.
- [ ] **Document known limitations:** Clearly define what the evaluator can and cannot reliably infer from a model's final response.

## Design principles

**Deterministic where possible.** Arithmetic and other predictable operations should use tools with explicit behavior rather than relying on the LLM to calculate correctly.

**Evaluate independently.** The agent's claim of success is not sufficient evidence that a task passed.

**Bound execution.** Agent loops need explicit limits and visible failure behavior.

**Preserve evidence.** Traces should make failures diagnosable and support repeatable experiments.

**Measure before optimizing.** Changes to prompts, models, and execution strategies should be evaluated against a consistent baseline.

## Limitations

- The initial dataset is small and arithmetic-focused.
- A local model's behavior may vary across executions.
- Numeric answer matching does not establish correctness for arbitrary natural-language tasks.
- The current prototype does not yet establish production-grade security, scalability, or reliability.
- Latency measurements depend on local hardware, model loading, and runtime conditions.

## Future direction

The longer-term goal is to evolve this prototype into a reusable evaluation and observability framework for tool-using agents, with richer benchmark scenarios, model comparisons, failure analysis, and regression detection.

The emphasis is on turning agent reliability from an informal impression into something engineers can test, measure, investigate, and improve.

---

**Status:** Active development  
**Scope:** Local-first agent evaluation and observability  
**License:** To be determined
