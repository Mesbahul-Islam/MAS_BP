from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
# ZeroMQ telemetry channel configuration
TELEMETRY_ENDPOINT = "tcp://127.0.0.1:5590"
TELEMETRY_TOPIC = "telemetry.truck"
TELEMETRY_OUTPUT_DIR = "outputs/telemetry_logs"
TELEMETRY_PUBLISH_EVERY_TICKS = 10

# ZeroMQ monitoring topic configuration (same endpoint as telemetry)
MONITORING_TOPIC = "monitoring.snapshot"
MONITORING_OUTPUT_DIR = "outputs/monitoring_logs"

# Simulation runtime configuration
SIM_NUM_TRUCKS = 2
SIM_SEED = 42
SIM_TICK_SECONDS = 0.0
SIM_MAX_TICKS = 0  # 0 means run continuously
SIM_PUBSUB_STARTUP_DELAY_SECONDS = 0.2

LLM_CALL_TIMEOUT_TICKS = 50
# Choose one scenario.
# "normal": both trucks go A -> C
# "deviation": truck 0 goes A -> B -> C, truck 1 goes A -> C
# "anomaly_stop_open_at_d": truck 0 stops at D, opens door briefly, then continues
# "cargo_state": truck 0 gradually increases temperature and CO2
SIM_ACTIVE_SCENARIO = "deviation"

# Fixed routes per truck for each scenario.
SIM_SCENARIOS = {
    "normal": [
        ["A", "C"],
        ["A", "C"],
    ],
    "deviation": [
        ["A", "B", "D", "C"],
        ["A", "C"],
    ],
    "anomaly_stop_open_at_d": [
        ["A", "B", "D", "C"],
        ["A", "C"],
    ],
    "cargo_state": [
        ["A", "B", "C"],
        ["A", "C"],
    ],
}


ROUTE_ANALYSIS_AGENT_PROMPT = """
You are a route and movement anomaly detection agent for freight trucks.Based on the telemetry snapshot provided, determine if there is an anomaly related to the truck's route or movement. 
            Focus on identifying potential issues such as unexpected stops, unusually slow speeds, or inconsistencies in movement patterns. 
            Provide a hypothesis with confidence level and evidence from the snapshot.
            Return a JSON object with the following format: {\"hypothesis\": \"...\", \"confidence\": 0.0, \"evidence\": \"...\"}"
"""