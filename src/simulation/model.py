from config import (
    MONITORING_TOPIC,
    SIM_ACTIVE_SCENARIO,
    SIM_NUM_TRUCKS,
    SIM_SCENARIOS,
    TELEMETRY_ENDPOINT,
    TELEMETRY_TOPIC,
    MONITORING_OUTPUT_DIR,
    ROUTE_ANALYSIS_TOPIC,
    CARGO_SAFETY_TOPIC,
    ORCHESTRATOR_TOPIC,
    MAS_HISTORY_TOPIC,
)
from mesa import Model
from mesa.space import ContinuousSpace

from simulation.agents.truck_agent import TruckAgent
from simulation.agents.monitoring_agent import MonitoringAgent
from simulation.agents.orchestrator_agent import OrchestratorAgent
from simulation.communication import ZeroMQTelemetryChannel
from simulation.nodes import NODE_COORDINATES, ROUTES
from simulation.agents.monitoring_agent import MonitoringAgent
from simulation.schemas import TRUCK_TELEMETRY_SCHEMA
from simulation.communication import run_telemetry_subscriber


class FreightSimulationModel(Model):
    """Minimal model that manages only truck agents and ticking."""

    def __init__(
        self,
        rng=None,
        seed=None,
    ):
        if rng is None and seed is not None:
            rng = seed
        super().__init__(rng=rng)
        
        self.num_trucks = SIM_NUM_TRUCKS
        self.running = True
        self.latest_monitoring_payload = None
        self.route_analysis_hypotheses = []
        self.cargo_safety_hypotheses = []
        self.orchestrator_verdicts = []
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

        # telemetry pub/sub channel (ZeroMQ).
        self.telemetry_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=TELEMETRY_TOPIC,
            schema=TRUCK_TELEMETRY_SCHEMA,
        )
        self.monitoring_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MONITORING_TOPIC,
            schema=None,
        )
        
        # Output channels for inter-agent communication
        self.route_analysis_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=ROUTE_ANALYSIS_TOPIC,
            schema=None,
        )
        self.cargo_safety_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=CARGO_SAFETY_TOPIC,
            schema=None,
        )
        self.orchestrator_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=ORCHESTRATOR_TOPIC,
            schema=None,
        )
        self.mas_history_channel = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MAS_HISTORY_TOPIC,
            schema=None,
        )

        # Create trucks, passing the per-agent `route` sequence so each agent gets its own route.
        TruckAgent.create_agents(
            model=self,
            n=self.num_trucks,
            route=routes_for_trucks,
            telemetry_channel=self.telemetry_channel,
        )

        # First created truck is treated as the bad truck for anomaly scenarios.
        truck_ids = [agent.fields.truck_id for agent in self.agents if isinstance(agent, TruckAgent)]
        self.bad_truck_id = min(truck_ids) if truck_ids else None

        MonitoringAgent(
            self,
            telemetry_channel=self.telemetry_channel,
            monitoring_channel=self.monitoring_channel,
        )
        
        OrchestratorAgent(self, output_channel=self.orchestrator_channel, history_channel=self.mas_history_channel)

        # Place all agents in the renderer-backed space.
        for agent in self.agents:
           if isinstance(agent, TruckAgent):
            self.space.place_agent(agent, agent.fields.position)

        self.mas_history = []  # Store historical data for visualization or analysis
    
    def step(self):
        if not self.running:
            return

        # Advance global tick first so agents see current tick during their step.
        self.tick += 1
        self.agents.do("step")

        if self._all_trucks_reached_goal():
            self.running = False

    def _all_trucks_reached_goal(self):
        trucks = [agent for agent in self.agents if isinstance(agent, TruckAgent)]
        if not trucks:
            return False

        return all(
            truck.fields.current_route_index >= len(truck.fields.route) - 1
            for truck in trucks
        )

    def close(self):
        """Release ZeroMQ telemetry resources."""
        self.telemetry_channel.close()
        self.monitoring_channel.close()
        self.route_analysis_channel.close()
        self.cargo_safety_channel.close()
        self.orchestrator_channel.close()
        self.mas_history_channel.close()

