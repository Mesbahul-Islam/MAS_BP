from mesa import Agent
from config import TELEMETRY_PUBLISH_EVERY_TICKS
from simulation.agents.truck_agent import TruckAgent
from simulation.communication import ZeroMQTelemetryChannel

class MonitoringAgent(Agent):
    
    def __init__(self, model, telemetry_channel, monitoring_channel):
        super().__init__(model)
        self.agent_name = f"monitoring_{self.unique_id}"
        self.telemetry_channel = telemetry_channel
        self.monitoring_channel = monitoring_channel

    def step(self):
        snapshots = []
        current_tick = getattr(self.model, "tick", 0)

        if current_tick % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
            return
        
        for agent in self.model.agents:
            if isinstance(agent, TruckAgent):

                telemetry_snapshot = {
                    "truck_id": str(agent.fields.truck_id),
                    "cargo_type": agent.fields.cargo_type,
                    "tick": current_tick,
                    "position": [agent.fields.position[0], agent.fields.position[1]],
                    "speed_kmh": agent.fields.speed_kmh,
                    "temperature_c": agent.fields.temperature_c,
                    "co2_ppm": agent.fields.co2_ppm,
                    "door_open": agent.fields.door_open,
                }


                analysis_snapshot = {
                    "truck_id": telemetry_snapshot["truck_id"],
                    "tick": telemetry_snapshot["tick"],
                    "telemetry_snapshot": telemetry_snapshot,
                }
                
                snapshots.append(analysis_snapshot)

        # Aggregate and publish to monitoring channel
        if snapshots:
            aggregated_payload = {
                "tick": current_tick,
                "snapshots": snapshots,
            }
            
            self.monitoring_channel.publish(
                tick=current_tick,
                source_agent=self.agent_name,
                payload=aggregated_payload,
            )

                

