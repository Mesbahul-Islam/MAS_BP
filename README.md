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
