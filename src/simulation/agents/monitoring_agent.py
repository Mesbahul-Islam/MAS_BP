from mesa import Agent
from simulation.agents.truck_agent import TruckAgent
from simulation.schemas import TruckTelemetryPayload

class MonitoringAgent(Agent):
    
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        
        for agent in self.model.agents:
            if isinstance(agent, TruckAgent):

                current_tick = getattr(self.model, "tick", 0)
                telemetry_snapshot: TruckTelemetryPayload = {
                    "truck_id": str(agent.fields.truck_id),
                    "cargo_type": agent.fields.cargo_type,
                    "tick": current_tick,
                    "position": [agent.fields.position[0], agent.fields.position[1]],
                    "speed_kmh": agent.fields.speed_kmh,
                    "temperature_c": agent.fields.temperature_c,
                    "co2_ppm": agent.fields.co2_ppm,
                    "door_open": agent.fields.door_open,
                }

                monitoring_snapshot = {
                    "truck_id": telemetry_snapshot["truck_id"],
                    "tick": telemetry_snapshot["tick"],
                    "speed": telemetry_snapshot["speed_kmh"] / 100.0,
                    "temperature": telemetry_snapshot["temperature_c"] / 50.0,
                    "co2": telemetry_snapshot["co2_ppm"] / 2000.0,
                    "door_open": 1 if telemetry_snapshot["door_open"] else 0,
                }

                analysis_snapshot = {
                    "truck_id": monitoring_snapshot["truck_id"],
                    "tick": monitoring_snapshot["tick"],
                    "monitoring_snapshot": monitoring_snapshot,
                    "telemetry_snapshot": telemetry_snapshot,
                }

                

