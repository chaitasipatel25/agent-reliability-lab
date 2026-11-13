# Agent Reliability Lab

**A local-first evaluation and observability framework for tool-using AI agents.**

Agent Reliability Lab explores a fundamental challenge in agentic systems: **how do we measure whether an AI agent is reliable, rather than simply trusting its final response?**

An agent may produce a plausible answer despite failing to use a required tool, receiving an execution error, or generating an incorrect result. This project makes those behaviors observable through execution traces, independent evaluation, and repeatable experiments.

## The Problem

Traditional unit tests validate individual components, but they don't fully capture the behavior of an AI agent interacting with tools.

Some important failure scenarios include:

- An agent returns an answer without using a required tool.
- A tool invocation fails because of invalid arguments or execution errors.
- An agent fails to recover after a tool failure.
- A tool executes successfully, but the agent produces an incorrect final answer.
- A prompt or model change introduces inconsistent results across executions.

Without structured evaluation, these failures can be difficult to identify and measure.

## The Solution

Build an evaluation harness that executes agent tasks, captures execution evidence, and independently evaluates outcomes.

The initial implementation uses a locally hosted Qwen3 model through Ollama and a deterministic calculator tool.

The system measures:

- **Answer correctness:** Does the final response match the expected answer?
- **Tool compliance:** Did the agent successfully execute a required tool?
- **Failure classification:** Did the task fail because of incorrect output, tool usage, tool execution, or agent execution?
- **Tool reliability:** How many tool calls succeeded or failed?
- **Recovery:** Could the agent complete a task after an earlier tool failure?
- **Execution performance:** How do pass rates and latency vary across repeated runs?

The evaluator operates independently of the agent, so the agent cannot determine its own success simply by claiming it completed a task.

## How It Works

```text

       Benchmark Dataset
              |
              v
        Evaluation Runner
              |
              v
           Agent Loop
              |
              v
       Local LLM (Ollama)
              |
              v
        Calculator Tool
              |
              v
      Execution Trace (JSON)
              |
              v
      Independent Evaluator
              |
              v
      Metrics & Failure Analysis
              |
              v
          JSON Reports
```



**Execution:** The runner loads benchmark tasks and invokes the model with the available tools.

**Tool interaction:** The agent can invoke the calculator. Tool results and errors are returned to the model, allowing it to continue execution within a bounded loop.

**Tracing:** Each execution captures tool calls, arguments, results, errors, timing, and the final response.

**Evaluation:** A deterministic evaluator checks the final answer, required tool execution, and execution errors. It also classifies failures and identifies successful recovery after tool failures.

**Repeated experiments:** Multiple evaluation runs produce individual reports, archived traces, and aggregate reliability metrics.

## Engineering Decisions

| Decision | Rationale |
|---|---|
| Local-first model execution | Run experiments without depending on a hosted LLM API |
| Deterministic tools | Use explicit, predictable execution for operations such as arithmetic |
| Independent evaluation | Avoid relying on the agent to judge its own correctness |
| Structured execution traces | Preserve evidence for debugging and failure analysis |
| Bounded agent execution | Prevent unbounded tool-call loops |
| Conservative failure classification | Distinguish tool invocation failures from tool execution failures |
| Repeated evaluations | Observe variability instead of relying on a single successful run |
| Automated tests | Validate execution and evaluation behavior without expensive model inference |

## Evaluation and Reliability Metrics

The evaluation harness generates metrics including:

| Metric | Description |
|---|---|
| Pass rate | Percentage of benchmark tasks completed successfully |
| Answer correctness | Whether the final response matches the expected result |
| Tool success rate | Successful tool calls divided by total tool calls |
| Tool failure count | Number of tool invocations that returned errors |
| Recovery count | Tasks completed successfully after a tool failure |
| Failure categories | Classification of unsuccessful tasks |
| Mean latency | Average task execution time |

The benchmark currently contains six arithmetic tasks. These metrics establish a baseline for the configured model and dataset; they are not a claim of general-purpose agent reliability.

## Running Locally

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/)
- Git

### 1. Download the model

```bash
ollama pull qwen3:8b
```

Make sure the Ollama service is running.

### 2. Set up the project

```bash
git clone https://github.com/chaitasipatel25/agent-reliability-lab
cd agent-reliability-lab

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install ollama pytest
```

### 3. Run automated tests

```bash
python -m pytest -v
```

The deterministic test suite validates calculator behavior, answer evaluation, failure classification, agent execution, and tool recovery without requiring model inference.

### 4. Run a single evaluation

```bash
python scripts/run_eval.py
```

### 5. Run repeated evaluations

```bash
python scripts/run_repeated_eval.py
```

Model evaluations require a running Ollama service and can take longer than unit tests.

## Observability Artifacts

The harness generates local JSON artifacts:

- `traces/` — execution traces for individual tasks.
- `traces/run_N/` — archived traces from individual repeated runs.
- `reports/latest.json` — most recent evaluation results.
- `reports/run_N.json` — individual repeated-run reports.
- `reports/repeated_summary.json` — aggregate metrics across runs.

Generated traces and reports are excluded from version control.

## Technology Stack

- **Language:** Python
- **Model runtime:** Ollama
- **Model:** Qwen3 8B
- **Testing:** pytest
- **Data and reporting:** JSON, JSONL
- **CI:** GitHub Actions

## Future Work

- Expand benchmarks to multi-step and more realistic tool-use scenarios.
- Compare models, prompts, and agent configurations against the same dataset.
- Improve trace structure and step-level observability.
- Integrate OpenTelemetry and an agent-tracing platform such as Arize Phoenix.
- Add regression detection across model and prompt changes.
- Improve packaging and reproducibility.

## Limitations

This is an early-stage prototype, not a production-grade agent evaluation platform.

The initial benchmark is small and arithmetic-focused. Numeric answer matching cannot establish correctness for arbitrary natural-language tasks, and local model behavior may vary between executions.

The goal is to establish a practical foundation for measuring, investigating, and improving the reliability of tool-using agents.

## License

MIT
