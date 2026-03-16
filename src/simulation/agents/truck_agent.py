from __future__ import annotations

from dataclasses import dataclass
import random

from mesa import Agent


@dataclass
class TruckFields:
    truck_id: str
    cargo_type: str
    route: list[str]
    position: tuple[float, float]
    speed_kmh: float
    temperature_c: float
    co2_ppm: float
    door_open: bool
    comm_online: bool


class TruckAgent(Agent):
    """Minimal truck agent with only core simulation fields."""

    def __init__(self,model):
        super().__init__(model)
        self.fields = TruckFields(
            truck_id=self.unique_id,
            cargo_type=random.choice(["pharma_refrigerated", "electronics", "furniture"]),
            route=["Node-A", "Node-B", "Node-C"],
            position=(0.0, 0.0),
            speed_kmh=0.0,
            temperature_c=20.0,
            co2_ppm=400.0,
            door_open=False,
            comm_online=True,
        )
    def say_hi(self) -> None:
        print (f"Hi, I'm truck {self.fields.truck_id} carrying {self.fields.cargo_type}!")
    