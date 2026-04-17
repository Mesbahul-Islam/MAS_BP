from __future__ import annotations

import os
import threading

import matplotlib.patches as patches
import mesa.visualization.solara_viz as solara_viz_module
from mesa.visualization import CommandConsole, SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle

from config import (
    SIM_SEED,
    TELEMETRY_ENDPOINT,
    TELEMETRY_OUTPUT_DIR,
    TELEMETRY_TOPIC,
)
from simulation.communication import run_telemetry_subscriber
from simulation.agents.truck_agent import TruckAgent
from simulation.model import FreightSimulationModel
from simulation.nodes import NODE_COORDINATES, ROUTES

CARGO_COLORS = {
    "Electronics": "tab:blue",
    "Furniture": "tab:orange",
    "Food": "tab:green",
    "Clothing": "tab:red",
    "Machinery": "tab:purple",
}


def _ensure_background_subscriber() -> None:
    """Start one telemetry subscriber per process for app-driven runs."""
    if os.environ.get("TELEMETRY_SUBSCRIBER_STARTED") == "1":
        return

    thread = threading.Thread(
        target=run_telemetry_subscriber,
        kwargs={
            "endpoint": TELEMETRY_ENDPOINT,
            "topic": TELEMETRY_TOPIC,
            "output_root": TELEMETRY_OUTPUT_DIR,
        },
        daemon=True,
        name="telemetry-subscriber",
    )
    thread.start()
    os.environ["TELEMETRY_SUBSCRIBER_STARTED"] = "1"


def _wide_grid_layout(num_components: int):
    """Use full-width, tall cards so the map fills the page."""
    return [
        {
            "i": i,
            "w": 12,
            "h": 30,
            "moved": False,
            "x": 0,
            "y": 30 * i,
        }
        for i in range(num_components)
    ]


def truck_portrayal(agent):
    if agent is None or not isinstance(agent, TruckAgent):
        return None

    return AgentPortrayalStyle(
        marker="o",
        color=CARGO_COLORS.get(agent.fields.cargo_type, "black"),
        size=50,
        zorder=3,
    )


def post_process_space(ax):
    ax.figure.set_size_inches(20, 10)
    ax.figure.set_dpi(120)
    ax.figure.set_constrained_layout(False)
    if hasattr(ax.figure, "set_layout_engine"):
        ax.figure.set_layout_engine("constrained")
    
    # Use full axes area instead of preserving equal aspect ratio (which can letterbox).
    ax.set_aspect("auto")
    ax.set_title("Freight Truck Map")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    x_values = [coords[0] for coords in NODE_COORDINATES.values()]
    y_values = [coords[1] for coords in NODE_COORDINATES.values()]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_margin = (x_max - x_min) * 0.08 if x_max != x_min else 10.0
    y_margin = (y_max - y_min) * 0.08 if y_max != y_min else 10.0
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    ax.margins(x=0, y=0)

    # Draw all route segments in the background.
    for route in ROUTES:
        route_points = [NODE_COORDINATES[node] for node in route]
        xs = [point[0] for point in route_points]
        ys = [point[1] for point in route_points]
        (line,) = ax.plot(xs, ys, color="lightgray", linestyle="--", linewidth=1.2, zorder=1)
        line.set_gid("static_route")

    # Draw node markers and labels.
    for node, (x, y) in NODE_COORDINATES.items():
        rect = patches.Rectangle((x - 10, y - 10), 20, 20, linewidth=1, edgecolor='black', facecolor='black', zorder=2)
        rect.set_gid("static_node")
        ax.add_patch(rect)
        node_label = ax.text(x + 40, y + 20, node, fontsize=8, color="black")
        node_label.set_gid("static_node_label")


model_params = {
    "seed": {
        "type": "InputText",
        "value": SIM_SEED,
        "label": "Random Seed",
    },
}

_ensure_background_subscriber()

model = FreightSimulationModel(rng=SIM_SEED)

# Make the Solara cards fill available width/height.
solara_viz_module.make_initial_grid_layout = _wide_grid_layout

renderer = SpaceRenderer(
    model,
    backend="matplotlib",
).setup_agents(truck_portrayal)
renderer.post_process = post_process_space
# Trigger an initial artist build so agent markers remain visible after first tick.
renderer.draw_agents()

page = SolaraViz(
    model,
    renderer,
    components=[CommandConsole],
    model_params=model_params,
    name="Freight Simulation Map",
)

page
