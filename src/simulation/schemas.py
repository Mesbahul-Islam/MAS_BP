from __future__ import annotations

from typing import Any, TypedDict


TRUCK_TELEMETRY_SCHEMA = "truck.telemetry.v1"


class TruckTelemetryPayload(TypedDict):
    """telemetry payload emitted by truck agents."""

    truck_id: str
    cargo_type: str
    tick: int
    position: list[float]
    speed_kmh: float
    temperature_c: float
    co2_ppm: float
    door_open: bool


class AgentEvent(TypedDict):
    """Telemetry event envelope for truck messages."""

    schema: str
    message_id: int
    timestamp_utc: str
    tick: int
    source_agent: str
    payload: dict[str, Any]