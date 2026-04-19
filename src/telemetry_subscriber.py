from config import MONITORING_OUTPUT_DIR, MONITORING_TOPIC, TELEMETRY_ENDPOINT
from simulation.communication import run_telemetry_subscriber


def main():
    run_telemetry_subscriber(
        endpoint=TELEMETRY_ENDPOINT,
        topic=MONITORING_TOPIC,
        output_root=MONITORING_OUTPUT_DIR,
    )


if __name__ == "__main__":
    main()
