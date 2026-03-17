from __future__ import annotations

from mesa import Model

from simulation.agents.truck_agent import TruckAgent
from simulation.nodes import ROUTES



class FreightSimulationModel(Model):
    """Minimal model that manages only truck agents and ticking."""

    def __init__(self, num_trucks: int, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        
        self.num_trucks = num_trucks
        # Simulation tick counter (increments each model.step())
        self.tick = 0

        # Candidate routes for trucks. If there are more trucks than routes, routes will be reused in round-robin.
        candidate_routes = ROUTES

        # Assign a route to each truck. If there are more trucks than candidate routes,
        # routes will be reused in round-robin.
        routes_for_trucks = [candidate_routes[i % len(candidate_routes)] for i in range(self.num_trucks)]

        # Create trucks, passing the per-agent `route` sequence so each agent gets its own route.
        TruckAgent.create_agents(model=self, n=self.num_trucks, route=routes_for_trucks)
    
    def step(self):
        # Advance global tick first so agents see current tick during their step.
        self.tick += 1
        self.agents.shuffle_do("step")
