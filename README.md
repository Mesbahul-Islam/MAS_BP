# MAS_BP

Minimal Mesa freight simulation prototype.

Current implementation includes only:

- `TruckAgent` with core fields
- `FreightSimulationModel` 

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Simulation

Run from repository root:

```bash
python run_simulation.py
```

Change tick limit, number of trucks, tick duration and status update parameters by using 

```
python run_simulation.py --max-ticks {tick} --tick-seconds {seconds} --num-trucks {num_trucks} --status-every {interval}
```


## Project Structure

```text
src/
	run_simulation.py
	simulation/
		model.py
		agents/
			truck_agent.py
```

## Notes

- One `TruckAgent` represents one shipment.
