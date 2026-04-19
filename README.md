# MAS_BP

Multi-agent freight simulation built with Mesa, with live map visualization in Solara and ZeroMQ-based event streaming.

## Current Features

- Truck movement across route nodes on a continuous space map.
- Monitoring agent that aggregates truck snapshots and publishes monitoring events.
- Shared ZeroMQ endpoint with separate topics for truck telemetry and monitoring snapshots.
- Monitoring output persistence to file, with automatic file reset for new runs.
- Scenario-based route and anomaly behavior selection from config.
- Simulation auto-stop when all trucks reach their final node.

## Setup

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

## Run Modes

Run headless simulation:

```bash
python src/run_simulation.py
```

Run Solara app:

```bash
solara run src/app.py
```

Then open the URL printed by Solara (usually http://localhost:8765).

## Runtime Behavior

- Tick duration is configured via SIM_TICK_SECONDS in [src/config.py](src/config.py).
- Telemetry publish interval is controlled by TELEMETRY_PUBLISH_EVERY_TICKS in [src/config.py](src/config.py).
- Monitoring snapshots are also published on the same tick interval.
- Simulation stops automatically when all trucks reach their destination nodes.

## Topics and Logging

- Endpoint: TELEMETRY_ENDPOINT in [src/config.py](src/config.py)
- Truck topic: TELEMETRY_TOPIC
- Monitoring topic: MONITORING_TOPIC

Only monitoring-topic messages are currently persisted by the subscriber flow.

Output file:

- [outputs/monitoring_logs/output.json](outputs/monitoring_logs/output.json)

Log reset behavior:

- File is cleared when subscriber starts.
- File is cleared again if incoming tick value goes backward, which indicates a new simulation run.

## Scenario Selection

Set active scenario in [src/config.py](src/config.py):

- normal
- deviation
- anomaly_stop_open_at_d

Current anomaly behavior for anomaly_stop_open_at_d:

- The designated bad truck is truck 0 (first created truck).
- At node D, it stops and opens door for 30 ticks.
- Door then closes.
- Truck resumes movement afterward.

## Key Files

- [src/config.py](src/config.py): runtime settings, topics, scenarios.
- [src/run_simulation.py](src/run_simulation.py): headless runner.
- [src/app.py](src/app.py): Solara map app.
- [src/telemetry_subscriber.py](src/telemetry_subscriber.py): monitoring-topic subscriber entrypoint.
- [src/simulation/model.py](src/simulation/model.py): model orchestration and stop condition.
- [src/simulation/agents/truck_agent.py](src/simulation/agents/truck_agent.py): truck movement and anomaly logic.
- [src/simulation/agents/monitoring_agent.py](src/simulation/agents/monitoring_agent.py): aggregate monitoring snapshots.
- [src/simulation/communication.py](src/simulation/communication.py): ZeroMQ channel and subscriber logging.
