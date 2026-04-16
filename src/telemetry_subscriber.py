from __future__ import annotations

from config import TELEMETRY_ENDPOINT, TELEMETRY_OUTPUT_DIR, TELEMETRY_TOPIC
from simulation.communication import run_telemetry_subscriber


def main() -> None:
    run_telemetry_subscriber(
        endpoint=TELEMETRY_ENDPOINT,
        topic=TELEMETRY_TOPIC,
        output_root=TELEMETRY_OUTPUT_DIR,
    )


if __name__ == "__main__":
    main()
