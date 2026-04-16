from __future__ import annotations

from dataclasses import dataclass
import random
from mesa import Agent
from simulation.communication import ZeroMQTelemetryChannel
from simulation.nodes import NODE_COORDINATES


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
    current_route_index: int

CARGO_TYPES = ["Electronics", "Furniture", "Food", "Clothing", "Machinery"]

class TruckAgent(Agent):
    """truck agent with only core simulation fields."""

    def __init__(self, model, route: list[str], telemetry_channel: ZeroMQTelemetryChannel):
        super().__init__(model)
        self.telemetry_channel = telemetry_channel
        self.agent_name = f"truck_{self.unique_id}"
        self.fields = TruckFields(
            truck_id=self.unique_id,
            cargo_type=random.choice(CARGO_TYPES),
            route=route,
            position=NODE_COORDINATES[route[0]],
            speed_kmh=random.uniform(60.0, 100.0),
            temperature_c=20.0,
            co2_ppm=400.0,
            door_open=False,
            comm_online=True,
            current_route_index=0,
        )

    def step(self):
        """
        Move the truck along its route based on its speed and update position. Actions taken per tick 
        """

        # If this truck already reached the final node, keep it parked.
        if self.fields.current_route_index >= len(self.fields.route) - 1:
            self.fields.speed_kmh = 0.0
            self.send_telemetry()
            return
        
        # Move towards the next point in the route.
        next_index = self.fields.current_route_index + 1
        # Keep track of current and next node
        current_node = self.fields.route[self.fields.current_route_index]
        next_node = self.fields.route[next_index]

        x, y = self.fields.position
        target_x, target_y = NODE_COORDINATES[next_node]

        # Convert km/h to km per simulation tick (1 tick = 1 minute).
        step_distance = self.fields.speed_kmh / 60.0
        delta_x = target_x - x
        delta_y = target_y - y
        remaining_distance = (delta_x**2 + delta_y**2) ** 0.5

        if remaining_distance <= step_distance:
            # Snap to next node when close enough and advance route pointer.
            self.fields.position = (target_x, target_y)
            self.model.space.move_agent(self, self.fields.position)
            self.fields.current_route_index = next_index
            self.send_telemetry()
            return

        # Ratio for proportional movement towards the next node.
        ratio = step_distance / remaining_distance
        self.fields.position = (round(x + delta_x * ratio, 2), round(y + delta_y * ratio, 2))
        self.model.space.move_agent(self, self.fields.position)
        self.send_telemetry()


    def send_telemetry(self):
        """Publish telemetry data over ZeroMQ pub/sub."""
        current_tick = getattr(self.model, "tick", 0)
        if self.fields.comm_online:
            telemetry_data = {
                "truck_id": self.fields.truck_id,
                "cargo_type": self.fields.cargo_type,
                "tick": current_tick,
                "position": self.fields.position,
                "speed_kmh": self.fields.speed_kmh,
                "temperature_c": self.fields.temperature_c,
                "co2_ppm": self.fields.co2_ppm,
                "door_open": self.fields.door_open,
            }
            self.telemetry_channel.publish(
                tick=current_tick,
                source_agent=self.agent_name,
                payload=telemetry_data,
            )

    
    