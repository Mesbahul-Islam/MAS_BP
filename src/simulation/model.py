from __future__ import annotations

import json
from pathlib import Path

from mesa import Model

from simulation.agents.truck_agent import TruckAgent


class FreightSimulationModel(Model):
    """Minimal model that manages only truck agents and ticking."""

    def __init__(self, num_trucks: int, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        
        self.num_trucks = num_trucks

        #Create trucks
        TruckAgent.create_agents(model=self, n=self.num_trucks)
    
    def step(self):
        self.agents.shuffle_do("say_hi")
