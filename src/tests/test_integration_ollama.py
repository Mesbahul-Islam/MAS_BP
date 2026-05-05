import pytest
from simulation.agents.decision_engine import DecisionEngine

@pytest.mark.integration
def test_decision_engine_actual_ollama():
    """
    Integration Testing Pattern:
    We construct the engine WITHOUT passing a mock LLM. It will fall back
    to ChatOllama("qwen3.5:0.8b") and attempt real TCP requests locally.
    """
    engine = DecisionEngine()
    
    # We construct a severely dangerous snapshot to ensure the LLM
    # inherently understands the context without us telling it directly.
    # This evaluates if the agent prompt accurately triggers a high risk score.
    dangerous_truck = {
        "truck_id": "1",
        "cargo_type": "Pharmaceuticals",
        "position": [10.0, 10.0],
        "speed_kmh": 0.0,
        "temperature_c": 45.0, # Highly dangerous for pharma
        "co2_ppm": 2000.0,
        "door_open": True
    }
    
    context = [{"tick": 1, "trucks": [dangerous_truck]}]
    
    # Invoking the real local LLM
    state = engine.evaluate(context)
    
    assert state.get("status") == "FINALIZED"
    
    # We expect the CargoAgent (and realistically the orchestrator) to 
    # panic and return a high risk score > 5.0
    proposals = state.get("proposals", [])
    assert len(proposals) >= 2, "Should have received proposals from agents"
    
    cargo_prop = next((p for p in proposals if p["sender"] == "CargoAgent"), None)
    assert cargo_prop is not None
    assert cargo_prop["risk_score"] > 5.0, "Ollama model failed to identify the anomaly as high risk"

