import pytest
import random
from typing import List
from dataclasses import dataclass
from config import SIM_SCENARIOS

class _MinimalTruckSim:
    """
    Self-contained minimal simulation that mirrors TruckAgent + MonitoringAgent
    logic without requiring Mesa, ZMQ, or a GPU.  Used as the 'simulation runner'
    in integration / eval tests below.
    """

    NODE_COORDS = {"A": (0.0, 0.0), "B": (100.0, 0.0), "C": (200.0, 0.0), "D": (100.0, 50.0)}

    @dataclass
    class TruckState:
        truck_id: str
        cargo_type: str
        route: List[str]
        position: tuple
        speed_kmh: float
        temperature_c: float = 20.0
        co2_ppm: float = 250.0
        door_open: bool = False
        comm_online: bool = True
        route_index: int = 0
        d_stop_ticks: int = 0
        d_stop_applied: bool = False
        cruise_speed: float = 0.0

        def __post_init__(self):
            self.cruise_speed = self.speed_kmh

    def __init__(self, scenario="normal", num_trucks=2, seed=42):
        random.seed(seed)
        self.scenario = scenario
        self.tick = 0
        self.telemetry_log: List[dict] = []
        self.verdict_log: List[dict] = []

        routes_for_trucks = SIM_SCENARIOS.get(scenario)
        if not routes_for_trucks:
            routes_for_trucks = {
                "normal": [["A", "B", "C"]],
                "deviation": [["A", "B", "D", "C"], ["A", "C"]],
                "anomaly_stop_open_at_d": [["A", "B", "D", "C"], ["A", "C"]],
                "cargo_state": [["A", "B", "C"]],
            }[scenario]

        self.trucks = []
        for i in range(num_trucks):
            route = routes_for_trucks[i % len(routes_for_trucks)]
            self.trucks.append(
                self.TruckState(
                    truck_id=str(i + 1),
                    cargo_type="Electronics",
                    route=route,
                    position=self.NODE_COORDS[route[0]],
                    speed_kmh=round(random.uniform(60, 100), 2),
                )
            )
        self.bad_truck_id = self.trucks[0].truck_id

    def _step_truck(self, t: "TruckState"):
        """Mirror TruckAgent.step() logic."""
        if self.scenario == "cargo_state" and t.truck_id == self.bad_truck_id:
            if t.temperature_c < 40.0:
                t.temperature_c = round(t.temperature_c + 0.025, 2)
            if t.co2_ppm < 1000.0:
                t.co2_ppm = round(t.co2_ppm + 1.2, 2)

        if self.scenario == "anomaly_stop_open_at_d" and t.truck_id == self.bad_truck_id:
            current_node = t.route[t.route_index]
            if t.d_stop_ticks > 0:
                t.speed_kmh = 0.0; t.door_open = True; t.comm_online = False
                t.d_stop_ticks -= 1
                return
            if t.d_stop_applied and t.door_open:
                t.door_open = False; t.speed_kmh = t.cruise_speed; t.comm_online = True
                return
            if current_node == "D" and not t.d_stop_applied:
                t.d_stop_applied = True; t.d_stop_ticks = 30
                t.speed_kmh = 0.0; t.door_open = True; t.comm_online = False
                return

        if t.route_index >= len(t.route) - 1:
            t.speed_kmh = 0.0; return

        next_idx = t.route_index + 1
        tx, ty = t.position
        nx, ny = self.NODE_COORDS[t.route[next_idx]]
        step = t.speed_kmh / 60.0
        dist = ((nx - tx) ** 2 + (ny - ty) ** 2) ** 0.5
        if dist <= step:
            t.position = (nx, ny); t.route_index = next_idx
            if t.route_index >= len(t.route) - 1:
                t.speed_kmh = 0.0
        else:
            r = step / dist
            t.position = (round(tx + (nx - tx) * r, 2), round(ty + (ny - ty) * r, 2))

    def run(self, max_ticks=500):
        for _ in range(max_ticks):
            self.tick += 1
            for t in self.trucks:
                self._step_truck(t)
            self.telemetry_log.append({
                "tick": self.tick,
                "trucks": [{
                    "truck_id": t.truck_id,
                    "position": list(t.position),
                    "speed_kmh": t.speed_kmh,
                    "temperature_c": t.temperature_c,
                    "co2_ppm": t.co2_ppm,
                    "door_open": t.door_open,
                    "comm_online": t.comm_online,
                } for t in self.trucks]
            })
            if all(t.route_index >= len(t.route) - 1 for t in self.trucks):
                break

    def all_arrived(self):
        return all(t.route_index >= len(t.route) - 1 for t in self.trucks)


def test_trucks_reach_destination_normal():
    sim = _MinimalTruckSim("normal", num_trucks=2)
    sim.run(max_ticks=500)
    assert sim.all_arrived()

def test_simulation_produces_telemetry():
    sim = _MinimalTruckSim("normal")
    sim.run(max_ticks=100)
    assert len(sim.telemetry_log) > 0

def test_bad_truck_stops_at_d():
    sim = _MinimalTruckSim("anomaly_stop_open_at_d", num_trucks=2)
    sim.run(max_ticks=500)
    door_open_ticks = [
        tick["tick"] for tick in sim.telemetry_log
        for truck in tick["trucks"]
        if truck["truck_id"] == sim.bad_truck_id and truck["door_open"]
    ]
    assert len(door_open_ticks) > 0, "Bad truck door should open at node D"

def test_good_truck_door_never_opens():
    sim = _MinimalTruckSim("anomaly_stop_open_at_d", num_trucks=2)
    sim.run(max_ticks=500)
    good_id = next(t.truck_id for t in sim.trucks if t.truck_id != sim.bad_truck_id)
    door_open_ticks = [
        tick for tick in sim.telemetry_log
        for truck in tick["trucks"]
        if truck["truck_id"] == good_id and truck["door_open"]
    ]
    assert door_open_ticks == [], "Good truck door should never open"

def test_cargo_state_temperature_rises():
    sim = _MinimalTruckSim("cargo_state", num_trucks=2)
    sim.run(max_ticks=200)
    final_temps = {
        truck["truck_id"]: truck["temperature_c"]
        for tick in sim.telemetry_log[-1:]
        for truck in tick["trucks"]
    }
    assert final_temps[sim.bad_truck_id] > 20.0

def test_cargo_state_co2_rises():
    sim = _MinimalTruckSim("cargo_state", num_trucks=2)
    sim.run(max_ticks=200)
    final_co2 = {
        truck["truck_id"]: truck["co2_ppm"]
        for tick in sim.telemetry_log[-1:]
        for truck in tick["trucks"]
    }
    assert final_co2[sim.bad_truck_id] > 250.0

def test_position_moves_monotonically_towards_goal():
    sim = _MinimalTruckSim("normal", num_trucks=1)
    sim.run(max_ticks=50)
    truck_id = sim.trucks[0].truck_id
    positions = [
        tick["trucks"][0]["position"][0]
        for tick in sim.telemetry_log
        if tick["trucks"][0]["truck_id"] == truck_id
    ]
    for i in range(len(positions) - 1):
        assert round(positions[i + 1], 1) >= round(positions[i], 1) - 0.1

def test_speed_is_zero_at_destination():
    sim = _MinimalTruckSim("normal", num_trucks=2)
    sim.run(max_ticks=1000)
    for t in sim.trucks:
        assert t.speed_kmh == 0.0

def test_comm_offline_during_d_stop():
    sim = _MinimalTruckSim("anomaly_stop_open_at_d", num_trucks=2)
    sim.run(max_ticks=500)
    offline_ticks = [
        tick["tick"] for tick in sim.telemetry_log
        for truck in tick["trucks"]
        if truck["truck_id"] == sim.bad_truck_id and not truck["comm_online"]
    ]
    assert len(offline_ticks) > 0

def test_monitoring_payload_structure():
    sim = _MinimalTruckSim("normal", num_trucks=2)
    sim.run(max_ticks=5)
    payload = sim.telemetry_log[-1]
    assert "tick" in payload
    assert "trucks" in payload
    for truck in payload["trucks"]:
        for key in ("truck_id", "position", "speed_kmh", "temperature_c", "co2_ppm", "door_open"):
            assert key in truck