# MAS_BP

Multi-agent freight simulation built with Mesa, with live map visualization in Solara and ZeroMQ-based event streaming.

## Current Features

- Truck movement across route nodes on a continuous space map.
- Monitoring agent that aggregates truck snapshots and publishes monitoring events.
- Shared ZeroMQ endpoint with separate topics for truck telemetry and monitoring snapshots.
- Monitoring output persistence to file, with automatic file reset for new runs.
- Scenario-based route and anomaly behavior selection from config.
- Simulation auto-stop when all trucks reach their final node.

## Project Setup

### Prerequisites

- Python 3.10+.
- A working virtual environment tool such as `venv`.
- For the LLM-backed integration tests and decision engine, a local Ollama installation with the `qwen3.5:0.8b` model available.

### Create and activate the environment

From repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows CMD:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Optional Ollama setup

If you want to run the real LLM integration path, start Ollama locally and make sure the required model is available:

```bash
ollama pull qwen3.5:0.8b
ollama serve
```

The test harness and decision engine use the local Ollama endpoint through `langchain-ollama`.

## Running the project

Run headless simulation:

```bash
python src/run_simulation.py
```

Run Solara app:

```bash
solara run src/app.py
```

Then open the URL printed by Solara (usually http://localhost:8765).

## Runtime behavior

- Tick duration is configured via SIM_TICK_SECONDS in [src/config.py](src/config.py).
- Telemetry publish interval is controlled by TELEMETRY_PUBLISH_EVERY_TICKS in [src/config.py](src/config.py).
- Monitoring snapshots are also published on the same tick interval.
- Simulation stops automatically when all trucks reach their destination nodes.

## Topics and logging

- Endpoint: TELEMETRY_ENDPOINT in [src/config.py](src/config.py)
- Truck topic: TELEMETRY_TOPIC
- Monitoring topic: MONITORING_TOPIC

Only monitoring-topic messages are currently persisted by the subscriber flow.

Output file:

- [outputs/monitoring_logs/output.json](outputs/monitoring_logs/output.json)

Log reset behavior:

- File is cleared when subscriber starts.
- File is cleared again if incoming tick value goes backward, which indicates a new simulation run.

## Scenario selection

Set active scenario in [src/config.py](src/config.py):

- normal
- deviation
- anomaly_stop_open_at_d

Current anomaly behavior for anomaly_stop_open_at_d:

- The designated bad truck is truck 0 (first created truck).
- At node D, it stops and opens door for 30 ticks.
- Door then closes.
- Truck resumes movement afterward.

## Testing

Run the default test suite:

```bash
PYTHONPATH=src python -m pytest -q
```

Run the integration tests that use the real Ollama-backed evaluation harness:

```bash
RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py -q -s
```

To enforce the timing thresholds during the timing evaluation, add:

```bash
ENFORCE_TIMING=1 RUN_INTEGRATION_TESTS=1 PYTHONPATH=src python -m pytest src/tests/test_evaluation_metrics.py::test_llm_detection_and_response_time -q -s
```

The timing test writes its report to [outputs/llm_scenario_timing_report.md](outputs/llm_scenario_timing_report.md), and the detection test writes its report to [outputs/llm_scenario_metrics_report.md](outputs/llm_scenario_metrics_report.md).

## Environment variables

- `OLLAMA_BASE_URL`: URL to your local or remote Ollama instance (default: `http://localhost:11434`).
- `OLLAMA_MODEL`: the Ollama model to use for decision engine (default: `qwen3.5:0.8b`).
- `RUN_INTEGRATION_TESTS`: enables the real Ollama/LangGraph integration path during pytest runs.
- `ENFORCE_TIMING`: when set to `1`, fails the timing test if the simulated-tick thresholds are exceeded.
- `PYTHONPATH`: set to `src` so the project package can be imported directly during local runs.

## Key Files

- [src/config.py](src/config.py): runtime settings, topics, scenarios.
- [src/run_simulation.py](src/run_simulation.py): headless runner.
- [src/app.py](src/app.py): Solara map app.
- [src/telemetry_subscriber.py](src/telemetry_subscriber.py): monitoring-topic subscriber entrypoint.
- [src/simulation/model.py](src/simulation/model.py): model orchestration and stop condition.
- [src/simulation/agents/truck_agent.py](src/simulation/agents/truck_agent.py): truck movement and anomaly logic.
- [src/simulation/agents/monitoring_agent.py](src/simulation/agents/monitoring_agent.py): aggregate monitoring snapshots.
- [src/simulation/communication.py](src/simulation/communication.py): ZeroMQ channel and subscriber logging.
