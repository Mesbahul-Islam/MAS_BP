# MAS_BP

MAS_BP is a multi-agent freight monitoring simulation built with Mesa, LangGraph, ZeroMQ, and Solara.
It simulates truck telemetry, publishes live monitoring data, and uses a LangGraph decision engine to produce
route and cargo safety analysis plus an orchestrator verdict.

## What You Can Do

- Run a headless freight simulation.
- Launch a Solara web app with a live simulation map and a decision dashboard.
- Switch between the map and dashboard without crashing the UI.
- Inspect the latest orchestrator verdict and agent reasoning for the most recent simulation tick.
- Persist dashboard history to a local JSON file for the active session.

## Main Features

- Continuous truck movement on a route network with scenario-based behavior.
- Telemetry streaming over ZeroMQ.
- Monitoring snapshots and analysis history published on separate topics.
- A Solara dashboard that shows only the latest tick, grouped by iteration.
- A Google Generative AI based decision engine for route, cargo, and orchestrator reasoning.
- Automatic clearing of dashboard history when the app starts.

## Requirements

- Python 3.10 or newer.
- A virtual environment tool such as `venv`.
- A valid Google API key for the LangChain Google Generative AI backend.
- Network access to Google Generative AI if you are running the live decision engine.

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

The app reads a `.env` file from the project root.

Create a file named `.env` in the repository root and add:

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.0-flash
```

Optional runtime variables used by the test suite and local runs:

- `RUN_INTEGRATION_TESTS=1` enables tests that talk to the real model backend.
- `ENFORCE_TIMING=1` makes the timing test fail if the response is too slow.
- `PYTHONPATH=src` is useful when running Python modules directly from the repository root.

If `GOOGLE_MODEL` is omitted, the default is `gemini-2.0-flash`.
If `GOOGLE_API_KEY` is missing, the decision engine will raise an error at startup.

## Running the Project

### Run the Solara app

```bash
solara run src/app.py
```

Open the URL printed by Solara, usually:

```text
http://localhost:8765
```

The app contains two tabs:

- Simulation Map: the live Mesa/Solara visualization.
- MAS Decision Dashboard: the latest agent negotiation result for the most recent tick.

### Run the headless simulation

```bash
python src/run_simulation.py
```

## How the Dashboard Works

- The dashboard listens to the `analysis.history` ZeroMQ topic.
- It keeps only the latest tick in view.
- Proposals are grouped by iteration and sorted by agent name.
- The orchestrator verdict is shown as a highlighted card on the right.
- The dashboard history file is stored at `outputs/dashboard_history.json`.
- The dashboard history is cleared when the app starts, so each run begins with a fresh view.

## Data Flow

- Truck telemetry is published on `telemetry.truck`.
- Monitoring snapshots are published on `monitoring.snapshot`.
- Agent history is published on `analysis.history`.
- The Solara app starts a background monitoring subscriber for live map support.
- The dashboard subscribes to history updates and renders the most recent tick only.

## Scenarios

Choose the active scenario in [`src/config.py`](src/config.py).

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

## Output Files

Important generated files:

- [`outputs/dashboard_history.json`](outputs/dashboard_history.json): latest dashboard history persisted between tab switches and app refreshes.
- [`outputs/monitoring_logs/output.json`](outputs/monitoring_logs/output.json): monitoring subscriber output.
- [`outputs/llm_scenario_metrics_report.md`](outputs/llm_scenario_metrics_report.md): evaluation metrics report.
- [`outputs/llm_scenario_timing_report.md`](outputs/llm_scenario_timing_report.md): timing report.

## Testing

Run the default test suite:

```bash
PYTHONPATH=src python -m pytest -q
```

Run the real-model integration tests:

```bash
RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py -q -s
```

Run the timing check with enforcement enabled:

```bash
ENFORCE_TIMING=1 RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py::test_llm_detection_and_response_time -q -s
```

## Key Files

- [`src/config.py`](src/config.py): runtime settings, scenario definitions, topics, and environment loading.
- [`src/app.py`](src/app.py): Solara entry point with tabbed UI.
- [`src/run_simulation.py`](src/run_simulation.py): headless simulation entry point.
- [`src/telemetry_subscriber.py`](src/telemetry_subscriber.py): monitoring log subscriber entry point.
- [`src/simulation/model.py`](src/simulation/model.py): Mesa model orchestration and stop condition.
- [`src/simulation/communication.py`](src/simulation/communication.py): ZeroMQ channels and subscriber helpers.
- [`src/simulation/agents/decision_engine.py`](src/simulation/agents/decision_engine.py): Google GenAI LangGraph decision engine.
- [`src/ui/dashboard.py`](src/ui/dashboard.py): dashboard rendering and history handling.

## Troubleshooting

### The app says `GOOGLE_API_KEY is not set`

Add the key to your `.env` file or export it in your shell before starting the app.

### The dashboard shows no data

Make sure the simulation is running and that the history topic is being published.
The dashboard only displays the latest tick that has been received.

### The map or dashboard freezes when switching tabs

The current implementation renders only the active tab to avoid cross-tab re-render conflicts.
If you still see issues, restart the app and start from a clean browser session.

### I changed `.env` but nothing happened

Restart the Solara app after editing environment variables. The values are loaded when the process starts.

## Project Summary

This project combines:

- Mesa for agent-based simulation.
- ZeroMQ for telemetry and history streaming.
- Solara for the web UI.
- LangGraph for multi-agent reasoning and negotiation.
- LangChain Google Generative AI for the live decision engine.

If you want to extend the system, start with `src/config.py` for runtime settings and `src/simulation/agents/decision_engine.py` for agent behavior.
