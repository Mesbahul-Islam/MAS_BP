from __future__ import annotations

import argparse
import time

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
    parser = argparse.ArgumentParser(description="Run real-time freight simulation.")
    parser.add_argument("--num-trucks", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--tick-seconds",
        type=float,
        default=60.0,
        help="Real-time duration of one simulation tick (default: 60 seconds).",
    )
    parser.add_argument(
        "--status-every",
        type=int,
        default=5,
        help="How many ticks between ordered status prints (default: 5).",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=0,
        help="Optional stop after N ticks. Use 0 to run continuously.",
    )
    args = parser.parse_args()

    model = FreightSimulationModel(num_trucks=args.num_trucks, seed=args.seed)

    print("Starting simulation (Ctrl+C to stop)...")
    try:
        while args.max_ticks <= 0 or model.tick < args.max_ticks:
            tick_start = time.monotonic()
            model.step()

            if model.tick % args.status_every == 0:
                print_tick_summary(model)

            elapsed = time.monotonic() - tick_start
            sleep_for = max(0.0, args.tick_seconds - elapsed)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        print("Simulation stopped by user.")

if __name__ == "__main__":
    main()
