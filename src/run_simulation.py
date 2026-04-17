from __future__ import annotations

import time

from config import (
    SIM_MAX_TICKS,
    SIM_PUBSUB_STARTUP_DELAY_SECONDS,
    SIM_SEED,
    SIM_TICK_SECONDS,
)
from simulation.model import FreightSimulationModel
from simulation.agents.truck_agent import TruckAgent


def print_tick_summary(model: FreightSimulationModel) -> None:
    trucks = sorted([agent for agent in model.agents if isinstance(agent, TruckAgent)], key=lambda truck: truck.fields.truck_id)
    print(f"Tick {model.tick:05d}")
    for truck in trucks:
        route_index = truck.fields.current_route_index
        current_node = truck.fields.route[route_index]
        position = truck.fields.position
        print(
            f"  Truck {truck.fields.truck_id:02d} | node={current_node} | "
            f"position=({position[0]:.2f}, {position[1]:.2f}) | "
            f"cargo={truck.fields.cargo_type}"
        )
    print()


def main():
    model = FreightSimulationModel(rng=SIM_SEED)

    # Allow PUB/SUB sockets to establish before first telemetry events are sent.
    time.sleep(SIM_PUBSUB_STARTUP_DELAY_SECONDS)

    try:
        while SIM_MAX_TICKS <= 0 or model.tick < SIM_MAX_TICKS:
            tick_start = time.monotonic()
            model.step()

            elapsed = time.monotonic() - tick_start
            sleep_for = max(0.0, SIM_TICK_SECONDS - elapsed)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        pass
    finally:
        model.close()

if __name__ == "__main__":
    main()
