from __future__ import annotations

# Shared coordinate map for all simulation nodes.
NODE_COORDINATES: dict[str, tuple[float, float]] = {
    "Node-A": (0.0, 0.0),
    "Node-B": (100.0, 0.0),
    "Node-C": (300.0, 0.0),
    "Node-D": (500.0, 80.0),
    "Node-E": (150.0, 80.0),
    "Node-F": (250.0, 80.0),
    "Node-G": (0.0, 150.0),
    "Node-H": (100.0, 150.0),
    "Node-I": (200.0, 150.0),
    "Node-J": (300.0, 150.0),
}

ROUTES = [
            ["Node-A", "Node-B", "Node-C"],
            ["Node-G", "Node-H", "Node-I"],
            ["Node-A", "Node-D", "Node-E", "Node-F"],
            ["Node-J", "Node-I", "Node-F"],
            ["Node-B", "Node-E", "Node-H"],
            ["Node-C", "Node-F", "Node-J"],
        ]