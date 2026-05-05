import json
import pytest
from unittest.mock import MagicMock
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage

def _make_mock_agent(response_json: dict):
    agent = MagicMock()
    msg = AIMessage(content=json.dumps(response_json))
    agent.invoke.return_value = {"messages": [msg]}
    # If the app tries to access structured_response (as it does), we should mock it too
    class MockOutput:
        pass
    mock_out = MockOutput()
    for k, v in response_json.items():
        setattr(mock_out, k, v)
        
    setattr(mock_out, "model_dump", lambda: response_json)
    agent.invoke.return_value["structured_response"] = mock_out
    return agent

def _run_agent_node(agent, sender_name, state):
    from simulation.agents.decision_engine import DecisionEngine
    de = DecisionEngine.__new__(DecisionEngine)
    de.route_agent = agent
    de.cargo_agent = agent
    de.orchestrator_agent = agent
    
    if sender_name == "RouteAgent":
        return de._route_agent_node(state)
    elif sender_name == "CargoAgent":
        return de._cargo_agent_node(state)
    else:
        return de._agent_node(state, agent, sender_name)

def test_route_agent_low_risk_normal_scenario(make_context):
    agent = _make_mock_agent({
        "hypothesis": "All trucks on expected route.",
        "proposed_action": "No action required.",
        "risk_score": 1,
    })
    state = {"context": make_context(), "tick": 10, "proposals": [], "iteration": 0, "feedback": ""}
    result = _run_agent_node(agent, "RouteAgent", state)
    assert result["proposals"][0]["risk_score"] == 1

def test_cargo_agent_high_risk_anomaly_scenario(make_context):
    agent = _make_mock_agent({
        "hypothesis": "Truck 2 door open and CO2 elevated.",
        "proposed_action": "Alert driver and dispatch.",
        "risk_score": 8,
    })
    state = {"context": make_context(), "tick": 10, "proposals": [], "iteration": 0, "feedback": ""}
    result = _run_agent_node(agent, "CargoAgent", state)
    assert result["proposals"][0]["risk_score"] == 8
    assert "door" in result["proposals"][0]["content"]["hypothesis"].lower()

def test_agent_response_contains_required_keys(make_context):
    response = {"hypothesis": "H", "proposed_action": "A", "risk_score": 5}
    agent = _make_mock_agent(response)
    state = {"context": make_context(), "tick": 5, "proposals": [], "iteration": 0, "feedback": ""}
    result = _run_agent_node(agent, "RouteAgent", state)
    p = result["proposals"][0]
    assert "hypothesis" in p["content"]
    assert "action" in p["content"]
    assert "risk_score" in p

def test_agent_risk_score_within_bounds(make_context):
    for score in [1, 5, 10]:
        agent = _make_mock_agent({"hypothesis": "H", "proposed_action": "A", "risk_score": score})
        state = {"context": make_context(), "tick": 1, "proposals": [], "iteration": 0, "feedback": ""}
        result = _run_agent_node(agent, "TestAgent", state)
        assert 1 <= result["proposals"][0]["risk_score"] <= 10

def test_agent_error_handling_on_invalid_json():
    # If the JSON is invalid, the engine handles it natively by returning 0
    from simulation.agents.decision_engine import DecisionEngine
    agent = MagicMock()
    # Mock to throw attribute error mimicking missing structured property or bad json
    agent.invoke.side_effect = Exception("JSON Decode Error")
    
    de = DecisionEngine.__new__(DecisionEngine)
    state = {"context": [], "tick": 1, "proposals": [], "iteration": 0, "feedback": ""}
    res = de._agent_node(state, agent, "TestAgent")
    assert res["proposals"][0]["risk_score"] == 0

def test_orchestrator_no_risk_verdict():
    from simulation.agents.decision_engine import DecisionEngine
    de = DecisionEngine.__new__(DecisionEngine)
    state = {
        "context": [],
        "tick": 1,
        "iteration": 0,
        "proposals": [
            {"sender": "RouteAgent", "risk_score": 0, "iteration": 0, "content": {"hypothesis": "None", "action": "None"}},
            {"sender": "CargoAgent", "risk_score": 0, "iteration": 0, "content": {"hypothesis": "None", "action": "None"}},
        ]
    }
    
    result = de._orchestrator_node(state)
    assert result["verdict"]["verdict"] == "no_risk"

def test_orchestrator_identifies_highest_risk_agent():
    proposals = [
        {"sender": "RouteAgent", "risk_score": 3, "iteration": 0},
        {"sender": "CargoAgent", "risk_score": 8, "iteration": 0},
    ]
    highest = max(proposals, key=lambda p: p["risk_score"])
    assert highest["sender"] == "CargoAgent"

def test_orchestrator_renegotiation_on_high_risk():
    from simulation.agents.decision_engine import DecisionEngine
    de = DecisionEngine.__new__(DecisionEngine)
    state = {"verdict": None, "iteration": 0, "proposals": []}
    decision = de._should_continue(state)
    assert decision == "renegotiate"

def test_orchestrator_finalizes_after_max_iterations():
    from simulation.agents.decision_engine import DecisionEngine
    de = DecisionEngine.__new__(DecisionEngine)
    state = {"verdict": {"verdict": "High Risk"}, "iteration": 2}
    decision = de._should_continue(state)
    assert decision == "finalize"

def test_orchestrator_mock_full_pipeline(make_context):
    route_agent = _make_mock_agent({
        "hypothesis": "Truck deviated from route.",
        "proposed_action": "Reroute truck.",
        "risk_score": 6,
    })
    cargo_agent = _make_mock_agent({
        "hypothesis": "Door open detected.",
        "proposed_action": "Alert driver.",
        "risk_score": 7,
    })
    state = {"context": make_context(), "tick": 20, "proposals": [], "iteration": 0, "feedback": ""}
    route_result = _run_agent_node(route_agent, "RouteAgent", state)
    state["proposals"].extend(route_result["proposals"])
    cargo_result = _run_agent_node(cargo_agent, "CargoAgent", state)
    state["proposals"].extend(cargo_result["proposals"])

    highest = max(state["proposals"], key=lambda p: p["risk_score"])
    assert highest["sender"] == "CargoAgent"
    assert highest["risk_score"] == 7