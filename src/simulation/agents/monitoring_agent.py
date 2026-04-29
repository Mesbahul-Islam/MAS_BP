from mesa import Agent

from config import TELEMETRY_PUBLISH_EVERY_TICKS
from simulation.agents.truck_agent import TruckAgent


class MonitoringAgent(Agent):
    def __init__(self, model, telemetry_channel, monitoring_channel):
        super().__init__(model)
        self.agent_name = f"monitoring_{self.unique_id}"
        self.telemetry_channel = telemetry_channel
        self.monitoring_channel = monitoring_channel

    def step(self):
        current_tick = getattr(self.model, "tick", 0)
        if current_tick % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
            return

        entries = []
        for agent in self.model.agents:
            if not isinstance(agent, TruckAgent):
                continue

            telemetry_snapshot = {
                "truck_id": str(agent.fields.truck_id),
                "cargo_type": agent.fields.cargo_type,
                "position": [agent.fields.position[0], agent.fields.position[1]],
                "speed_kmh": agent.fields.speed_kmh,
                "temperature_c": agent.fields.temperature_c,
                "co2_ppm": agent.fields.co2_ppm,
                "door_open": agent.fields.door_open,
            }
            entries.append(telemetry_snapshot)

        if not entries:
            return

        self.model.latest_monitoring_payload = {
            "tick": current_tick,
            "payload": entries,
        }

        self.monitoring_channel.publish(
            tick=current_tick,
            source_agent=self.agent_name,
            payload=entries,
        )
