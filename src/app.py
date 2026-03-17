from __future__ import annotations

import mesa.visualization.solara_viz as solara_viz_module
from mesa.visualization import CommandConsole, Slider, SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle

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


def _wide_grid_layout(num_components: int):
    """Use full-width component cards so the space plot is significantly larger."""
    return [
        {
            "i": i,
            "w": 12,
            "h": 20,
            "moved": False,
            "x": 0,
            "y": 20 * i,
        }
        for i in range(num_components)
    ]


def truck_portrayal(agent):
    if agent is None or not isinstance(agent, TruckAgent):
        return None

    return AgentPortrayalStyle(
        marker="o",
        color=CARGO_COLORS.get(agent.fields.cargo_type, "black"),
        size=90,
        zorder=3,
    )


def post_process_space(ax):
    ax.figure.set_size_inches(20, 12)
    ax.figure.set_dpi(120)
    # Use full axes area instead of preserving equal aspect ratio (which can letterbox).
    ax.set_aspect("auto")
    ax.set_title("Freight Truck Map")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    x_values = [coords[0] for coords in NODE_COORDINATES.values()]
    y_values = [coords[1] for coords in NODE_COORDINATES.values()]
    x_margin = (max(x_values) - min(x_values)) * 0.03
    y_margin = (max(y_values) - min(y_values)) * 0.06
    ax.set_xlim(min(x_values) - x_margin, max(x_values) + x_margin)
    ax.set_ylim(min(y_values) - y_margin, max(y_values) + y_margin)
    ax.margins(x=0, y=0)

    # Draw all route segments in the background.
    for route in ROUTES:
        route_points = [NODE_COORDINATES[node] for node in route]
        xs = [point[0] for point in route_points]
        ys = [point[1] for point in route_points]
        ax.plot(xs, ys, color="lightgray", linestyle="--", linewidth=1.2, zorder=1)

    # Draw node markers and labels.
    for node, (x, y) in NODE_COORDINATES.items():
        ax.scatter(x, y, marker="s", s=80, color="black", zorder=2)
        ax.text(x + 40, y + 20, node, fontsize=8, color="black")


model_params = {
    "num_trucks": Slider("Number of Trucks", 4, 1, 20, 1),
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
}

model = FreightSimulationModel(num_trucks=4, seed=42)

# Override default SolaraViz card sizing to make the map canvas larger.
solara_viz_module.make_initial_grid_layout = _wide_grid_layout

renderer = SpaceRenderer(
    model,
    backend="matplotlib",
).setup_agents(truck_portrayal)
renderer.post_process = post_process_space
renderer.draw_agents()

page = SolaraViz(
    model,
    renderer,
    components=[CommandConsole],
    model_params=model_params,
    name="Freight Simulation Map",
)

page
