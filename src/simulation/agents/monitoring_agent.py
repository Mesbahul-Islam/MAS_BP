from mesa import Agent
from simulation.agents.truck_agent import TruckAgent

class MonitoringAgent(Agent):
    
    def __init__(self, model):
        super().__init__(model)

    def normalize(self, snapshot):
        return {
        "speed": snapshot["speed_kmh"] / 100,
        "temperature": snapshot["temperature_c"] / 50,
        "co2": snapshot["co2_ppm"] / 2000,
        "door_open": 1 if snapshot["door_open"] else 0
    }

    def step(self):
        
        for agent in self.model.agents:
            if isinstance(agent, TruckAgent):

                snapshot = {
                    "speed_kmh": agent.fields.speed_kmh,
                    "temperature_c": agent.fields.temperature_c,
                    "co2_ppm": agent.fields.co2_ppm,
                    "door_open": agent.fields.door_open
                }

                normalized = self.normalize(snapshot)

                print(f"Monitoring → Truck {agent.fields.truck_id}: {normalized}")

