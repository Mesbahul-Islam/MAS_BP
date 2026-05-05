import os
import threading
import solara
import pandas as pd

import matplotlib.patches as patches
import mesa.visualization.solara_viz as solara_viz_module
from mesa.visualization import CommandConsole, SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle

from config import (
    MONITORING_OUTPUT_DIR,
    MONITORING_TOPIC,
    SIM_SEED,
    TELEMETRY_ENDPOINT,
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


def _ensure_background_subscriber():
    """Start one telemetry subscriber per process for app-driven runs."""
    if os.environ.get("TELEMETRY_SUBSCRIBER_STARTED") == "1":
        return

    thread = threading.Thread(
        target=run_telemetry_subscriber,
        kwargs={
            "endpoint": TELEMETRY_ENDPOINT,
            "topic": MONITORING_TOPIC,
            "output_root": MONITORING_OUTPUT_DIR,
        },
        daemon=True,
        name="telemetry-subscriber",
    )
    thread.start()
    os.environ["TELEMETRY_SUBSCRIBER_STARTED"] = "1"


def _wide_grid_layout(num_components):
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
   if isinstance(agent, TruckAgent):

    return AgentPortrayalStyle(
        marker="o",
        color=CARGO_COLORS.get(agent.fields.cargo_type, "black"),
        size=50,
        zorder=3,
    )
    return AgentPortrayalStyle(marker="o", size=0)



def post_process_space(ax):
    # Solara manages figure layout; avoid figure-level resizing/layout mutations here.

    # Keep geometry readable while still filling panel space.
    ax.set_aspect("auto")
    ax.set_title("Freight Truck Map")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.figure.set_size_inches(14, 7)

    x_values = [coords[0] for coords in NODE_COORDINATES.values()]
    y_values = [coords[1] for coords in NODE_COORDINATES.values()]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_margin = (x_max - x_min) * 0.05 if x_max != x_min else 10.0
    y_margin = (y_max - y_min) * 0.05 if y_max != y_min else 10.0
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    ax.margins(x=0, y=0)

    # Remove previously drawn static artists so redraws do not accumulate stale objects.
    static_gids = {"static_route", "static_node", "static_node_label"}
    for line in list(ax.lines):
        if line.get_gid() in static_gids:
            line.remove()
    for patch in list(ax.patches):
        if patch.get_gid() in static_gids:
            patch.remove()
    for text in list(ax.texts):
        if text.get_gid() in static_gids:
            text.remove()

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
        node_label = ax.annotate(
            node,
            xy=(x, y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
            color="black",
        )
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
@solara.component
def Page():
    _ensure_background_subscriber()

    steps = solara.use_reactive(0)

    model = solara.use_memo(lambda: FreightSimulationModel(rng=SIM_SEED), [])

    renderer = solara.use_memo(lambda: SpaceRenderer(model, backend="matplotlib").setup_agents(truck_portrayal), [])
    renderer.post_process = post_process_space

    def on_step():
        steps.value = model.schedule.steps
    
    viz = SolaraViz(
        model,
        renderer,
        components=[CommandConsole],
        model_params=model_params,
        name="Freight Simulation Map",
    )

    with solara.Column(style={"padding": "20px"}):
        solara.Title("Freight Monitoring System")
        
        with solara.Card():
            viz 
        
        solara.Markdown("---")
        with solara.Card("Fleet Status Table"):
            truck_data = []
            for agent in model.agents:
                if isinstance(agent, TruckAgent):
                    truck_data.append({
                        "Truck ID": agent.fields.truck_id,
                        "Cargo": agent.fields.cargo_type,
                        "X": round(agent.fields.position[0], 1),
                        "Y": round(agent.fields.position[1], 1),
                        "Status": "Moving" if model.running else "Arrived"
                    })
            
            if truck_data:
                solara.DataFrame(pd.DataFrame(truck_data))
            else:
                solara.Info("Waiting for agents to initialize...")

        #Anomaly notification (if bad_truck_id exists)
        if hasattr(model, 'bad_truck_id') and model.bad_truck_id is not None:
             solara.Error(f"⚠️ ANOMALY DETECTED: Truck {model.bad_truck_id}")

page = Page


