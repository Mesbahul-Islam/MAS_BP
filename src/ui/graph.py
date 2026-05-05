import solara


def get_node_status(state, target_node, current_node):
    """Helper to determine the color of the node based on execution progress."""
    if target_node == current_node:
        return "active"
    else:
        return "pending"


@solara.component
def nodes(name, status):
    
    colors = {
        "active": {"bg": "#fff3cd", "border": "#ffc107", "text": "#856404"},     # Yellow
        "completed": {"bg": "#d4edda", "border": "#28a745", "text": "#155724"},  # Green
        "pending": {"bg": "#f8f9fa", "border": "#ccc", "text": "#6c757d"},       # Gray
    }

    c = colors[status]

    style = f"""
        padding: 10px 20px; 
        background: {c['bg']}; 
        border: 2px solid {c['border']}; 
        color: {c['text']};
        text-align: center;
        width: 10vw;
        """
    return solara.HTML(tag="div", unsafe_innerHTML=name, style=style)

@solara.component
def Graph(state):
    proposals = state.get("proposals", [])
    current_iter = state.get("iteration", 0)
    verdict = state.get("verdict")

    # Filter proposals for the current iteration
    current_proposals = [p for p in proposals if p.get("iteration") == current_iter]
    
    if verdict is not None:
        current_node = "Orchestrator"
    elif len(current_proposals) == 0:
        current_node = "RouteAgent"
    elif len(current_proposals) == 1:
        current_node = "CargoAgent"
    else:
        current_node = "Orchestrator"

    with solara.Row(justify="center"):

        with solara.Column(gap="50px", align="center"):
            nodes("RouteAgent", get_node_status(state, "RouteAgent", current_node))
            with solara.Row(gap="50px", justify="space-between"):
                nodes("CargoAgent", get_node_status(state, "CargoAgent", current_node))
                nodes("Orchestrator", get_node_status(state, "Orchestrator", current_node))
        