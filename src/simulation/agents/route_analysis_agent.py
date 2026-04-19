from mesa import Agent
from config import TELEMETRY_PUBLISH_EVERY_TICKS


class RouteAnalysisAgent(Agent):
    """Rule-based scaffold for route and movement anomaly hypotheses.

    Replace `analyze_snapshot` internals with an LLM call later.
    """

    def __init__(self, model):
        super().__init__(model)
        self.agent_name = f"route_analysis_{self.unique_id}"

    def step(self):
        current_tick = getattr(self.model, "tick", 0)
        if current_tick % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
            return

        monitoring_payload = getattr(self.model, "latest_monitoring_payload", None)
        if not monitoring_payload or monitoring_payload.get("tick") != current_tick:
            self.model.route_analysis_hypotheses = []
            return

        hypotheses = []
        for snapshot in monitoring_payload.get("snapshots", []):
            hypothesis = self.analyze_snapshot(snapshot)
            if hypothesis is not None:
                hypotheses.append(hypothesis)

        self.model.route_analysis_hypotheses = hypotheses

    def analyze_snapshot(self, snapshot):
        telemetry = snapshot.get("telemetry_snapshot", {})
        truck_id = str(telemetry.get("truck_id", ""))
        speed_kmh = telemetry.get("speed_kmh", 0.0)
        door_open = telemetry.get("door_open", False)
        tick = telemetry.get("tick", getattr(self.model, "tick", 0))

        evidence = []
        confidence = 0.0

        # Placeholder movement risk rules for scaffold behavior.
        if door_open and speed_kmh > 1.0:
            evidence.append("Door is open while truck is moving.")
            confidence = max(confidence, 0.85)

        if speed_kmh < 0.1:
            evidence.append("Truck speed is near zero.")
            confidence = max(confidence, 0.45)

        if not evidence:
            return None

        severity = "high" if confidence >= 0.8 else "medium"

        return {
            "hypothesis_id": f"route-{truck_id}-{tick}",
            "truck_id": truck_id,
            "tick": tick,
            "source_agent": self.agent_name,
            "anomaly_type": "route_or_movement_risk",
            "severity": severity,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "recommended_actions": [
                "Verify route progress and stop reason.",
                "Contact driver and request status update.",
            ],
        }
