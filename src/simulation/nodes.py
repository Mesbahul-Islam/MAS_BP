from __future__ import annotations

# Shared coordinate map for all simulation nodes.
NODE_COORDINATES: dict[str, tuple[float, float]] = {
    "Node-A": (0.0, 0.0),
    "Node-B": (10.0, 0.0),
    "Node-C": (20.0, 0.0),
    "Node-D": (5.0, 8.0),
    "Node-E": (15.0, 8.0),
    "Node-F": (25.0, 8.0),
    "Node-G": (0.0, 15.0),
    "Node-H": (10.0, 15.0),
    "Node-I": (20.0, 15.0),
    "Node-J": (30.0, 15.0),
}

ROUTES = [
            ["Node-A", "Node-B", "Node-C"],
            ["Node-G", "Node-H", "Node-I"],
            ["Node-A", "Node-D", "Node-E", "Node-F"],
            ["Node-J", "Node-I", "Node-F"],
            ["Node-B", "Node-E", "Node-H"],
            ["Node-C", "Node-F", "Node-J"],
        ]