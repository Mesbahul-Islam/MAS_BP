import random
from mesa import Agent
from config import SIM_ACTIVE_SCENARIO, TELEMETRY_PUBLISH_EVERY_TICKS
from simulation.communication import ZeroMQTelemetryChannel
from simulation.nodes import NODE_COORDINATES

class TruckFields:
    def __init__(self, truck_id, cargo_type, route, position, speed_kmh, temperature_c, co2_ppm, door_open, comm_online, current_route_index):
        self.truck_id = truck_id
        self.cargo_type = cargo_type
        self.route = route
        self.position = position
        self.speed_kmh = speed_kmh
        self.cruise_speed_kmh = speed_kmh  # Store original speed for resuming after anomalies
        self.temperature_c = temperature_c
        self.co2_ppm = co2_ppm
        self.door_open = door_open
        self.comm_online = comm_online
        self.current_route_index = current_route_index
        self.d_stop_applied = False
        self.d_stop_ticks_remaining = 0

CARGO_TYPES = ["Electronics", "Furniture", "Food", "Clothing", "Machinery"]

class TruckAgent(Agent):
    """truck agent with only core simulation fields."""

    def __init__(self, model, route, telemetry_channel):
        super().__init__(model)
        self.telemetry_channel = telemetry_channel
        self.agent_name = f"truck_{self.unique_id}"
        self.fields = TruckFields(
            truck_id=self.unique_id,
            cargo_type=random.choice(CARGO_TYPES),
            route=route,
            position=NODE_COORDINATES[route[0]],
            speed_kmh=round(random.uniform(60.0, 100.0), 2),
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

        if self._handle_anomaly_scenario():
            return

        if self._handle_arrived_at_destination():
            return

        self._move_along_route()

    def _handle_anomaly_scenario(self):
        """Handle anomaly-specific behavior and return True when handled."""
        if SIM_ACTIVE_SCENARIO == "cargo_state":
            self._apply_cargo_state_anomaly()
            return False

        if (
            SIM_ACTIVE_SCENARIO != "anomaly_stop_open_at_d"
            or getattr(self.model, "bad_truck_id", None) != self.fields.truck_id
        ):
            return False

        current_node = self.fields.route[self.fields.current_route_index]

        # In anomaly scenario, the bad truck stops once at node D and opens its door briefly.
        # Phase 1: hold at D with door open for a fixed 30 ticks.
        if self.fields.d_stop_ticks_remaining > 0:
            self.fields.speed_kmh = 0.0
            self.fields.door_open = True
            self.fields.d_stop_ticks_remaining -= 1
            self.fields.comm_online = False
            self.send_telemetry()
            return True

        # Phase 2: close door once after the 30-tick hold, then resume next tick.
        if self.fields.d_stop_applied and self.fields.door_open:
            self.fields.door_open = False
            self.fields.speed_kmh = self.fields.cruise_speed_kmh
            self.send_telemetry()
            return True

        if current_node == "D" and not self.fields.d_stop_applied:
            self.fields.d_stop_applied = True
            self.fields.d_stop_ticks_remaining = 30
            self.fields.speed_kmh = 0.0
            self.fields.door_open = True
            self.fields.comm_online = False
            self.send_telemetry()
            return True

        return False

    def _apply_cargo_state_anomaly(self):
        """Simple cargo anomaly: gradually increase temperature and CO2."""
        is_bad_truck = getattr(self.model, "bad_truck_id", None) == self.fields.truck_id
        if not is_bad_truck:
            return
        
        if self.fields.temperature_c >= 40.0:
            self.fields.temperature_c = self.fields.temperature_c  # Cap temperature increase
        else:
            self.fields.temperature_c = round(self.fields.temperature_c + 0.025, 2)

        if self.fields.co2_ppm >= 1000.0:
            self.fields.co2_ppm = self.fields.co2_ppm  # Cap CO2 increase
        else:
            self.fields.co2_ppm = round(self.fields.co2_ppm + 1.2, 2)

    def _handle_arrived_at_destination(self):
        """Keep truck parked after reaching final route node."""
        if self.fields.current_route_index >= len(self.fields.route) - 1:
            self.fields.speed_kmh = 0.0
            self.send_telemetry()
            return True

        return False

    def _move_along_route(self):
        """Execute normal movement logic for active route progress."""
        # Move towards the next point in the route.
        next_index = self.fields.current_route_index + 1
        # Keep track of current and next node
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
        if current_tick % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
            return
        if self.fields.comm_online:
            telemetry_data = {
                "truck_id": str(self.fields.truck_id),
                "cargo_type": self.fields.cargo_type,
                "tick": current_tick,
                "position": [self.fields.position[0], self.fields.position[1]],
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

    
    