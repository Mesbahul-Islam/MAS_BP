from __future__ import annotations

from config import SIM_ACTIVE_SCENARIO, SIM_NUM_TRUCKS, SIM_SCENARIOS
from mesa import Model
from mesa.space import ContinuousSpace

from simulation.agents.truck_agent import TruckAgent
from simulation.communication import ZeroMQTelemetryChannel
from simulation.nodes import NODE_COORDINATES, ROUTES
from simulation.agents.monitoring_agent import MonitoringAgent



class FreightSimulationModel(Model):
    """Minimal model that manages only truck agents and ticking."""

    def __init__(
        self,
        rng=None,
        seed: int | None = None,
    ) -> None:
        if rng is None and seed is not None:
            rng = seed
        super().__init__(rng=rng)
        
        self.num_trucks = SIM_NUM_TRUCKS
        # Simulation tick counter (increments each model.step())
        self.tick = 0
        candidate_routes = SIM_SCENARIOS.get(SIM_ACTIVE_SCENARIO)
        if not candidate_routes:
            candidate_routes = ROUTES

        # Build a continuous map space using node coordinate bounds.
        x_values = [coords[0] for coords in NODE_COORDINATES.values()]
        y_values = [coords[1] for coords in NODE_COORDINATES.values()]
        self.space = ContinuousSpace(
            x_max=max(x_values) + 2,
            y_max=max(y_values) + 2,
            torus=False,
            x_min=min(x_values) - 2,
            y_min=min(y_values) - 2,
        )

        # Assign per-truck routes from selected scenario.
        routes_for_trucks = [candidate_routes[i % len(candidate_routes)] for i in range(self.num_trucks)]

        # Ephemeral telemetry pub/sub channel (ZeroMQ).
        self.telemetry_channel = ZeroMQTelemetryChannel()

        # Create trucks, passing the per-agent `route` sequence so each agent gets its own route.
        TruckAgent.create_agents(
            model=self,
            n=self.num_trucks,
            route=routes_for_trucks,
            telemetry_channel=self.telemetry_channel,
        )
        MonitoringAgent(self)

        # Place all agents in the renderer-backed space.
        for agent in self.agents:
           if isinstance(agent, TruckAgent):
            self.space.place_agent(agent, agent.fields.position)
    
    def step(self):
        # Advance global tick first so agents see current tick during their step.
        self.tick += 1
        self.agents.shuffle_do("step")

    def close(self) -> None:
        """Release ZeroMQ telemetry resources."""
        self.telemetry_channel.close()
