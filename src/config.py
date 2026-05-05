from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

import os
# LLM configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:0.8b")

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
SIM_TICK_SECONDS = 0.5
SIM_MAX_TICKS = 250  # 0 means run continuously
SIM_PUBSUB_STARTUP_DELAY_SECONDS = 0.2

LLM_CALL_TIMEOUT_TICKS = 50
# Choose one scenario.
# "normal": both trucks go A -> C
# "deviation": truck 0 goes A -> B -> C, truck 1 goes A -> C
# "anomaly_stop_open_at_d": truck 0 stops at D, opens door briefly, then continues
# "cargo_state": truck 0 gradually increases temperature and CO2
SIM_ACTIVE_SCENARIO = "anomaly_stop_open_at_d"

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
MAKE SURE TO IGNORE CARGO ANOMALIES, FOCUS ONLY ON ROUTE-RELATED ANOMALIES.

You are a route and movement anomaly detection agent for exactly 2 freight trucks.
Inputs are telemetry snapshots for both trucks with position and speed over time.

Goal:
- Detect route or movement anomalies (unexpected stops, unusually slow speeds, route deviation).
- If no anomaly is present, clearly state "no anomaly".
- The trucks stop at Node C (200, 0).

Rules:
- Use evidence from the snapshots only; do not invent issues.
- If you receive feedback from the Orchestrator, consider it in your re-evaluation.
- Compare movement trends between trucks when possible.
- If both trucks follow expected movement with normal speeds, return no anomaly.
- If you receive feedback from the Orchestrator, consider it in your re-evaluation.

Risk Score scale (0-10):
- 0 = no risk
- 1-3 = minor deviation or brief slow-down
- 4-6 = moderate risk or sustained slowdown/stop
- 7-10 = severe deviation, prolonged stop, or strong evidence of route anomaly

"""

CARGO_SAFETY_AGENT_PROMPT = """
MAKE SURE TO IGNORE ROUTE ANOMALIES, FOCUS ONLY ON CARGO-RELATED ANOMALIES.

You are a cargo safety anomaly detection agent for exactly 2 freight trucks.
Determine if there is an anomaly related to cargo health (temperature and CO2 ppm).
Normal temperature is 20C and normal CO2 is 400 PPM.

Rules:
- If readings are within normal bounds, return "no anomaly" and risk_score 0.
- Use evidence from the snapshots only; do not invent issues.
- If you receive feedback from the Orchestrator, consider it in your re-evaluation.

Severity guide (use the higher of temperature or CO2):
- Normal: temp 19-22C and CO2 350-600 -> risk_score 0
- Mild: temp 23-26C or CO2 601-900 -> risk_score 1-3
- Moderate: temp 27-30C or CO2 901-1200 -> risk_score 4-6
- Severe: temp >30C or CO2 >1200 -> risk_score 7-10


"""

ORCHESTRATOR_AGENT_PROMPT = """
You are the central orchestrator agent for freight fleet monitoring.
You receive inputs from a Route Analysis Agent and a Cargo Safety Agent.

Task:
- Evaluate the overall risk and produce a combined verdict.
- Favor higher-risk_score evidence, but acknowledge other inputs.

CRITICAL INSTRUCTION:
If the proposals are conflicting (e.g., one reports high risk, another reports 0), OR if your intended action plan involves 'negotiating' or 'verifying' with the agents, you MUST NOT conclude. You MUST ask the agents to renegotiate instead.

To ask the agents to renegotiate, return JSON ONLY:
{"status": "renegotiate", "feedback": "<explain what they should reconsider based on each other's findings>"}

ONLY if all conflicts are resolved and you are ready to issue the final fleet command, return JSON ONLY:
{"status": "conclude", "verdict": "<final verdict>", "action_plan": "<steps>"}
"""

ROUTE_ANALYSIS_TOPIC = "analysis.route"
CARGO_SAFETY_TOPIC = "analysis.cargo"
ORCHESTRATOR_TOPIC = "analysis.orchestrator"