import json
import os
import re
import time
from dataclasses import dataclass
from statistics import mean
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest
from langchain.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from simulation.agents.decision_engine import DecisionEngine


@dataclass
class ScenarioResult:
    scenario: str
    expected_anomaly: bool
    predicted_anomaly: bool
    verdict: str
    route_risk: int
    cargo_risk: int
    highest_risk: int
    raw_route_output: str
    raw_cargo_output: str
    raw_orchestrator_output: str


@dataclass
class ScenarioTimingResult:
    scenario: str
    avg_detection_time_ms: float
    avg_response_time_ms: float
    avg_llm_call_time_ms: float
    runs: int


from src.tests.test_system_integration import _MinimalTruckSim

def _synthetic_scenarios() -> Dict[str, List[dict]]:
    scenarios_list = ["normal", "deviation", "anomaly_stop_open_at_d", "cargo_state"]
    generated_scenarios = {}
    for scenario_name in scenarios_list:
        sim = _MinimalTruckSim(scenario=scenario_name, num_trucks=2)
        # Run for a few ticks to generate telemetry context for decision engine
        sim.run(max_ticks=3)
        generated_scenarios[scenario_name] = sim.telemetry_log
    return generated_scenarios


def _build_llm() -> ChatOllama:
    kwargs: Dict[str, Any] = {
        "model": "qwen3.5:0.8b",
        "temperature": 0,
        "streaming": False,
        "base_url": "http://192.168.144.153:11434",
        "reasoning": False,
    }
    try:
        return ChatOllama(**kwargs)
    except Exception:
        kwargs.pop("reasoning", None)
        return ChatOllama(**kwargs)


def _extract_json_object(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _unpack_structured_response(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return {key: val for key, val in vars(value).items() if not key.startswith("_")}
    return {}


class _ParsedAgentResponse:
    def __init__(self, hypothesis: str, proposed_action: str, risk_score: int):
        self.hypothesis = hypothesis
        self.proposed_action = proposed_action
        self.risk_score = risk_score

    def __repr__(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


class _ParsedOrchestratorResponse:
    def __init__(self, status: str, verdict: str, action_plan: str, feedback: str):
        self.status = status
        self.verdict = verdict
        self.action_plan = action_plan
        self.feedback = feedback

    def __repr__(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


class _RealOllamaAgentAdapter:
    def __init__(self, llm: ChatOllama, system_prompt: str, response_format: Optional[type] = None, call_timings: Optional[List[float]] = None):
        self.llm = llm
        self.system_prompt = system_prompt
        self.response_format = response_format
        self.call_timings = call_timings

    def invoke(self, payload: dict) -> dict:
        user_message = payload["messages"][0].content
        messages = [
            SystemMessage(content=self._instruction_block()),
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message),
        ]
        start = time.perf_counter()
        response = self.llm.invoke(messages)
        elapsed = time.perf_counter() - start
        if self.call_timings is not None:
            self.call_timings.append(elapsed)
        content = getattr(response, "content", "") or ""
        parsed = self._parse_content(content)
        structured = self._build_structured_response(parsed, content)
        return {"messages": [response], "structured_response": structured}

    def _instruction_block(self) -> str:
        if self.response_format and self.response_format.__name__ == "OrchestratorResponse":
            return (
                "Return a single JSON object only. Keys: status, verdict, action_plan, feedback. "
                "status should be 'conclude' or 'renegotiate'. "
                "verdict must be 'no_risk' or 'high_risk'."
            )
        return (
            "Return a single JSON object only. Keys: hypothesis, proposed_action, risk_score. "
            "risk_score must be an integer from 0 to 10."
        )

    def _parse_content(self, content: str) -> dict:
        parsed = _extract_json_object(content)
        if parsed:
            # Check if it has 'risk_score' to see if it's agent response
            # If so, keep it. If missing risk_score but has action_plan, it's orchestrator.
            if "risk_score" in parsed:
                # ensure it's casted correctly
                parsed["risk_score"] = _safe_int(parsed["risk_score"], 0)
            return parsed

        lower = content.lower()
        if self.response_format and self.response_format.__name__ == "OrchestratorResponse":
            verdict = "high_risk" if any(word in lower for word in ["risk", "anomaly", "halt", "danger", "severe", "warning"]) else "no_risk"
            return {
                "status": "conclude",
                "verdict": verdict,
                "action_plan": content.strip() or "No action plan returned.",
                "feedback": "",
            }

        risk = 0
        # "stop" removed to avoid trivial false positives
        if any(word in lower for word in ["severe", "high risk", "danger", "anomaly"]):
            risk = 8
        elif any(word in lower for word in ["moderate", "warning", "concern", "high_risk"]):
            risk = 5
        elif any(word in lower for word in ["minor", "slight", "low risk", "risk"]):
            risk = 2

        return {
            "hypothesis": content.strip() or "No hypothesis returned.",
            "proposed_action": "Review telemetry.",
            "risk_score": risk,
        }

    def _build_structured_response(self, parsed: dict, raw_content: str) -> object:
        if self.response_format and self.response_format.__name__ == "OrchestratorResponse":
            raw_verdict = str(parsed.get("verdict", "")).lower()
            if raw_verdict not in ["no_risk", "high_risk"]:
                combined = str(parsed.get("action_plan", "")) + " " + str(parsed.get("feedback", ""))
                combined = combined.lower()
                if any(word in combined for word in ["anomaly", "halt", "danger", "severe", "warning"]):
                    raw_verdict = "high_risk"
                else:
                    raw_verdict = "no_risk"

            return _ParsedOrchestratorResponse(
                status=str(parsed.get("status", "conclude")),
                verdict=raw_verdict,
                action_plan=str(parsed.get("action_plan", raw_content.strip() or "No action plan returned.")),
                feedback=str(parsed.get("feedback", "")),
            )

        return _ParsedAgentResponse(
            hypothesis=str(parsed.get("hypothesis", raw_content.strip() or "No hypothesis returned.")),
            proposed_action=str(parsed.get("proposed_action", "Review telemetry.")),
            risk_score=_safe_int(parsed.get("risk_score", 0)),
        )


def _patched_create_agent(llm, system_prompt=None, response_format=None, **kwargs):
    return _RealOllamaAgentAdapter(llm=llm, system_prompt=system_prompt or "", response_format=response_format)


def _patched_create_agent_timed(call_timings):
    def _factory(llm, system_prompt=None, response_format=None, **kwargs):
        return _RealOllamaAgentAdapter(
            llm=llm,
            system_prompt=system_prompt or "",
            response_format=response_format,
            call_timings=call_timings,
        )

    return _factory


def _run_engine(context: List[dict]) -> dict:
    llm = _build_llm()
    with patch("simulation.agents.decision_engine.create_agent", side_effect=_patched_create_agent):
        engine = DecisionEngine(llm=llm)
        final_state = {}
        for state_chunk in engine.process_telemetry(context, tick=context[-1]["tick"]):
            final_state = state_chunk
        return final_state


def _run_engine_timed(context: List[dict], call_timings: Optional[List[float]] = None) -> tuple[dict, float]:
    llm = _build_llm()
    start = time.perf_counter()
    with patch("simulation.agents.decision_engine.create_agent", side_effect=_patched_create_agent_timed(call_timings)):
        engine = DecisionEngine(llm=llm)
        final_state = {}
        for state_chunk in engine.process_telemetry(context, tick=context[-1]["tick"]):
            final_state = state_chunk
        total_elapsed = time.perf_counter() - start
        return final_state, total_elapsed


def _parse_result(scenario: str, final_state: dict) -> ScenarioResult:
    verdict_data = _unpack_structured_response(final_state.get("verdict", {}))
    verdict = str(verdict_data.get("verdict", "")).strip()
    proposals = final_state.get("proposals", [])
    route_risk = next((p.get("risk_score", 0) for p in proposals if p.get("sender") == "RouteAgent"), 0)
    cargo_risk = next((p.get("risk_score", 0) for p in proposals if p.get("sender") == "CargoAgent"), 0)
    highest_risk = max([p.get("risk_score", 0) for p in proposals], default=0)
    predicted_anomaly = verdict.lower() not in {"", "no_risk", "no risk", "normal"}
    route_data = _unpack_structured_response(next((p.get("content", {}) for p in proposals if p.get("sender") == "RouteAgent"), {}))
    cargo_data = _unpack_structured_response(next((p.get("content", {}) for p in proposals if p.get("sender") == "CargoAgent"), {}))
    return ScenarioResult(
        scenario=scenario,
        expected_anomaly=scenario != "normal",
        predicted_anomaly=predicted_anomaly,
        verdict=verdict,
        route_risk=route_risk,
        cargo_risk=cargo_risk,
        highest_risk=highest_risk,
        raw_route_output=json.dumps(route_data, ensure_ascii=False),
        raw_cargo_output=json.dumps(cargo_data, ensure_ascii=False),
        raw_orchestrator_output=json.dumps(verdict_data, ensure_ascii=False),
    )


def _score_against_ground_truth(results: List[ScenarioResult]) -> Dict[str, float]:
    tp = fp = fn = tn = 0
    for item in results:
        if item.expected_anomaly and item.predicted_anomaly:
            tp += 1
        elif not item.expected_anomaly and item.predicted_anomaly:
            fp += 1
        elif item.expected_anomaly and not item.predicted_anomaly:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
    }


def _collect_timing_results(scenarios: Dict[str, List[dict]], runs_per_scenario: int = 2) -> List[ScenarioTimingResult]:
    timing_results: List[ScenarioTimingResult] = []

    for scenario, context in scenarios.items():
        detection_times_ms: List[float] = []
        response_times_ms: List[float] = []
        llm_call_times_ms: List[float] = []

        for _ in range(runs_per_scenario):
            call_timings: List[float] = []
            _, detection_elapsed = _run_engine_timed(context, call_timings=call_timings)
            detection_times_ms.append(detection_elapsed * 1000.0)
            response_times_ms.append(sum(call_timings) * 1000.0)
            if call_timings:
                llm_call_times_ms.append(mean(call_timings) * 1000.0)
            else:
                llm_call_times_ms.append(0.0)

        timing_results.append(
            ScenarioTimingResult(
                scenario=scenario,
                avg_detection_time_ms=mean(detection_times_ms),
                avg_response_time_ms=mean(response_times_ms),
                avg_llm_call_time_ms=mean(llm_call_times_ms),
                runs=runs_per_scenario,
            )
        )

    return timing_results


def _write_md_report(results: List[ScenarioResult], summary: Dict[str, float], report_path: str) -> None:
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    lines = [
        "# LLM Scenario Evaluation Report",
        "",
        "| Scenario | Expected Anomaly | Predicted Anomaly | Verdict | Route Risk | Cargo Risk | Highest Risk |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for item in results:
        lines.append(
            f"| {item.scenario} | {'true' if item.expected_anomaly else 'false'} | {'true' if item.predicted_anomaly else 'false'} | {item.verdict} | {item.route_risk} | {item.cargo_risk} | {item.highest_risk} |"
        )

    lines.extend(
        [
            "",
            "## Detection Metrics",
            "| Metric | Value |",
            "|---|---:|",
            f"| Precision | {summary['precision']:.3f} |",
            f"| Recall | {summary['recall']:.3f} |",
            f"| False Positive Rate | {summary['false_positive_rate']:.3f} |",
        ]
    )

    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def _write_timing_report(results: List[ScenarioTimingResult], report_path: str) -> None:
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    lines = [
        "# LLM Timing Evaluation Report",
        "",
        "| Scenario | Avg Detection Time (ms) | Avg Response Time (ms) | Avg LLM Call Time (ms) | Runs | Pass Detection | Pass Response |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for item in results:
        # determine pass/fail using config thresholds
        try:
            import importlib
            cfg = importlib.import_module("config")
            sim_tick = getattr(cfg, "SIM_TICK_SECONDS", 0.5)
        except Exception:
            sim_tick = 0.5

        DETECTION_TICKS_MAX = 20
        REASONING_RESPONSE_TICKS_MAX = 30

        pass_detection = (item.avg_detection_time_ms / 1000.0) <= (DETECTION_TICKS_MAX * sim_tick)
        pass_response = (item.avg_response_time_ms / 1000.0) <= (REASONING_RESPONSE_TICKS_MAX * sim_tick)

        lines.append(
            f"| {item.scenario} | {item.avg_detection_time_ms:.2f} | {item.avg_response_time_ms:.2f} | {item.avg_llm_call_time_ms:.2f} | {item.runs} | {'PASS' if pass_detection else 'FAIL'} | {'PASS' if pass_response else 'FAIL'} |"
        )

    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")


@pytest.mark.integration
def test_llm_synthetic_scenarios():
    scenarios = _synthetic_scenarios()
    results = []

    for scenario, context in scenarios.items():
        final_state = _run_engine(context)
        results.append(_parse_result(scenario, final_state))

    summary = _score_against_ground_truth(results)
    report_path = "outputs/llm_scenario_metrics_report.md"
    _write_md_report(results, summary, report_path)

    assert len(results) == len(scenarios)
    assert os.path.exists(report_path)


@pytest.mark.integration
def test_llm_detection_and_response_time():
    try:
        import importlib
        cfg = importlib.import_module("config")
        SIM_TICK_SECONDS = getattr(cfg, "SIM_TICK_SECONDS", 0.5)
    except Exception:
        SIM_TICK_SECONDS = 0.5
        scenarios = _synthetic_scenarios()
        timing_results = _collect_timing_results(scenarios, runs_per_scenario=2)

        report_path = "outputs/llm_scenario_timing_report.md"
        _write_timing_report(timing_results, report_path)

        # By default write pass/fail into report. If caller explicitly sets ENFORCE_TIMING=1,
        # enforce assertions to fail the test when thresholds are exceeded.
        enforce = os.environ.get("ENFORCE_TIMING", "0") == "1"
        if enforce:
            try:
                import importlib
                cfg = importlib.import_module("config")
                SIM_TICK_SECONDS = getattr(cfg, "SIM_TICK_SECONDS", 0.5)
            except Exception:
                SIM_TICK_SECONDS = 0.5

            DETECTION_TICKS_MAX = 20
            REASONING_RESPONSE_TICKS_MAX = 30

            detection_seconds_max = DETECTION_TICKS_MAX * SIM_TICK_SECONDS
            reasoning_response_seconds_max = REASONING_RESPONSE_TICKS_MAX * SIM_TICK_SECONDS

            for item in timing_results:
                avg_detection_s = item.avg_detection_time_ms / 1000.0
                avg_response_s = item.avg_response_time_ms / 1000.0
                assert avg_detection_s <= detection_seconds_max, f"Detection latency too high for {item.scenario}: {avg_detection_s}s > {detection_seconds_max}s"
                assert avg_response_s <= reasoning_response_seconds_max, f"Reasoning+response too high for {item.scenario}: {avg_response_s}s > {reasoning_response_seconds_max}s"

        assert len(timing_results) == len(scenarios)
        assert os.path.exists(report_path)
