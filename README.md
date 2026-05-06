# MAS_BP

MAS_BP is a multi-agent freight monitoring simulation built with Mesa, ZeroMQ, Solara, LangGraph,
and LangChain Ollama.

It simulates truck telemetry, streams live monitoring data, and uses a three-agent decision engine
to produce route analysis, cargo safety analysis, and an orchestrator verdict.

## What This Project Does

- Simulates truck movement across a route network.
- Publishes telemetry and monitoring updates over ZeroMQ.
- Runs an Ollama-backed LangGraph decision pipeline.
- Shows a live Solara map and a decision dashboard.
- Persists dashboard history locally so the latest tick survives tab switching.

## Features

- Continuous-space truck movement and route progression.
- Monitoring snapshots for both trucks.
- Agent negotiation between Route, Cargo, and Orchestrator roles.
- A dashboard that shows only the latest tick, grouped by iteration.
- A verdict card that highlights the final orchestrator decision and action plan.
- Automatic dashboard history reset when the app starts.

## Requirements

- Python 3.10 or newer.
- A virtual environment tool such as `venv`.
- A local Ollama installation.
- The `qwen3.5:0.8b` model, or another model configured in `src/config.py`.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows CMD

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the repository root and add:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:0.8b
```

Optional variables:

- `RUN_INTEGRATION_TESTS=1` enables the real Ollama-backed integration path during pytest runs.
- `ENFORCE_TIMING=1` makes the timing test fail if thresholds are exceeded.
- `PYTHONPATH=src` is useful when running Python modules directly from the repository root.

If `OLLAMA_BASE_URL` is omitted, the default is `http://localhost:11434`.
If `OLLAMA_MODEL` is omitted, the default is `qwen3.5:0.8b`.

## Optional Ollama Setup

If you are running the real LLM path locally, start Ollama and pull the model first:

```bash
ollama pull qwen3.5:0.8b
ollama serve
```

The decision engine uses the local Ollama endpoint through `langchain-ollama`.

## Running the Project

### Run the Solara app

```bash
solara run src/app.py
```

Then open the URL printed by Solara, usually:

```text
http://localhost:8765
```

### Run the headless simulation

```bash
python src/run_simulation.py
```

## User Guide

### Simulation Map tab

The Simulation Map tab shows the live freight map and truck positions.
It is rendered only when the tab is active to avoid cross-tab render conflicts.

### MAS Decision Dashboard tab

The dashboard shows the latest tick only.
For that tick, it displays:

- the tick number,
- agent proposals grouped by iteration,
- the orchestrator verdict,
- the action plan,
- the agent that triggered the highest risk score.

If the simulation is not producing data yet, the dashboard shows a waiting message.

### History persistence

Dashboard history is saved to `outputs/dashboard_history.json`.
The file is cleared when the app starts so each new simulation session begins with a fresh history.

## Runtime Behavior

- Tick duration is configured in [`src/config.py`](src/config.py).
- Telemetry is published on the `telemetry.truck` topic.
- Monitoring snapshots are published on the `monitoring.snapshot` topic.
- Agent history is published on the `analysis.history` topic.
- The dashboard only renders the latest tick from its persisted history.
- The simulation stops automatically when all trucks reach their destination nodes.

## Scenarios

Set the active scenario in [`src/config.py`](src/config.py).

Available scenarios:

- `normal`
- `deviation`
- `anomaly_stop_open_at_d`
- `cargo_state`

### Scenario Notes

- `normal`: both trucks follow the expected route.
- `deviation`: one truck takes a longer route path.
- `anomaly_stop_open_at_d`: one truck stops at node D and opens its door briefly.
- `cargo_state`: the cargo telemetry changes over time.

## Testing

Run the default test suite:

```bash
PYTHONPATH=src python -m pytest -q
```

Run the real-model integration tests:

```bash
RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py -q -s
```

Run the timing test with enforcement enabled:

```bash
ENFORCE_TIMING=1 RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py::test_llm_detection_and_response_time -q -s
```

The timing test writes to [`outputs/llm_scenario_timing_report.md`](outputs/llm_scenario_timing_report.md).
The detection test writes to [`outputs/llm_scenario_metrics_report.md`](outputs/llm_scenario_metrics_report.md).

## Output Files

Important generated files:

- [`outputs/dashboard_history.json`](outputs/dashboard_history.json): latest dashboard history.
- [`outputs/monitoring_logs/output.json`](outputs/monitoring_logs/output.json): monitoring subscriber output.
- [`outputs/llm_scenario_timing_report.md`](outputs/llm_scenario_timing_report.md): timing report.
- [`outputs/llm_scenario_metrics_report.md`](outputs/llm_scenario_metrics_report.md): detection report.

## Key Files

- [`src/config.py`](src/config.py): runtime settings, environment loading, scenarios, topics, and prompts.
- [`src/app.py`](src/app.py): Solara app entry point.
- [`src/run_simulation.py`](src/run_simulation.py): headless simulation entry point.
- [`src/telemetry_subscriber.py`](src/telemetry_subscriber.py): monitoring subscriber entry point.
- [`src/simulation/model.py`](src/simulation/model.py): Mesa model orchestration and stop condition.
- [`src/simulation/agents/truck_agent.py`](src/simulation/agents/truck_agent.py): truck movement and anomaly logic.
- [`src/simulation/agents/monitoring_agent.py`](src/simulation/agents/monitoring_agent.py): monitoring snapshot aggregation.
- [`src/simulation/agents/decision_engine.py`](src/simulation/agents/decision_engine.py): Ollama decision engine and LangGraph negotiation.
- [`src/simulation/communication.py`](src/simulation/communication.py): ZeroMQ channel helpers.
- [`src/ui/dashboard.py`](src/ui/dashboard.py): dashboard rendering and history handling.

## Troubleshooting

### `OLLAMA_BASE_URL` or `OLLAMA_MODEL` is not set

Add the Ollama settings to `.env` or export them in your shell before launching the app.

### The dashboard shows no data

Make sure the simulation is running and publishing to `analysis.history`.
The dashboard only shows the latest tick that has been received.

### The map or dashboard freezes when switching tabs

The app renders only the active tab to avoid Solara re-render conflicts.
If you still see problems, restart the app and refresh the browser session.

### I changed `.env`, but nothing changed

Restart the Solara app after editing environment variables. They are loaded when the process starts.

## Notes for Developers

The decision engine uses `ChatOllama` from `langchain-ollama`.
The Ollama settings are loaded from `src/config.py`.

If you want to extend the simulation, the best entry points are:

- [`src/config.py`](src/config.py) for settings and prompts.
- [`src/simulation/agents/decision_engine.py`](src/simulation/agents/decision_engine.py) for agent behavior.
- [`src/ui/dashboard.py`](src/ui/dashboard.py) for dashboard presentation.
