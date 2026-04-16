from __future__ import annotations

# ZeroMQ telemetry channel configuration
TELEMETRY_ENDPOINT = "tcp://127.0.0.1:5590"
TELEMETRY_TOPIC = "telemetry.truck"
TELEMETRY_OUTPUT_DIR = "outputs/telemetry_logs"

# Simulation runtime configuration
SIM_NUM_TRUCKS = 4
SIM_SEED = 42
SIM_TICK_SECONDS = 0.0
SIM_MAX_TICKS = 0  # 0 means run continuously
SIM_PUBSUB_STARTUP_DELAY_SECONDS = 0.2
