# MAS_BP

Mesa freight simulation prototype with real-time ticking and Solara map visualization.

Current implementation includes only:

- `TruckAgent` movement along predefined routes
- `FreightSimulationModel` with global tick tracking
- Telemetry emission every 5 ticks
- Solara map view for live truck movement

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Windows Setup

From the repository root:

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Command Prompt (CMD):

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation scripts, run this once in PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Run Simulation

Run from repository root:

```bash
python src/run_simulation.py
```

Real-time mode uses `1 tick = 60 seconds` by default. Stop with `Ctrl+C`.

Change tick limit, number of trucks, tick duration and status update interval using:

```bash
python src/run_simulation.py --max-ticks {ticks} --tick-seconds {seconds} --num-trucks {num_trucks} --status-every {interval}
```

Quick test example:

```bash
python src/run_simulation.py --max-ticks 10 --tick-seconds 0.01 --status-every 5
```

Windows example:

```powershell
python src/run_simulation.py --max-ticks 10 --tick-seconds 0.01 --status-every 5
```

## Run Solara Map

Run from repository root:

```bash
solara run src/app.py
```

Windows example:

```powershell
solara run src/app.py
```

Then open the local URL printed by Solara (usually `http://localhost:8765`).

The map view shows:

- Node locations and labels
- Route lines
- Moving truck markers (color-coded by cargo type)


## Project Structure

```text
src/
	app.py
	run_simulation.py
	simulation/
		model.py
		nodes.py
		agents/
			truck_agent.py
```

## Notes

- One `TruckAgent` represents one shipment.
- Telemetry is emitted every 5 simulation ticks.
