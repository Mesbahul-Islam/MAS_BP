import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolCall
from simulation.agents.decision_engine import DecisionEngine

def test_decision_engine_unit_fake_chat_model():
    """
    Test using LangChain's GenericFakeChatModel (Unit Testing Pattern).
    We mock the model to yield fake responses containing the structured
    output kwargs so we can test the state machine purely offline.
    """
    # Since create_agent with response_format translates to structured output
    # via tool calling in LangChain, we mock the exact parsed output. If it uses
    # JSON mode, it parses the content string. Ollama with 'format="json"' usually
    # outputs JSON strings. We must simulate what ChatOllama returns.
    
    from simulation.agents.decision_engine import AgentResponse, OrchestratorResponse
    
    class MockAgent:
        def __init__(self, response_obj):
            self.response_obj = response_obj
        def invoke(self, *args, **kwargs):
            return {"structured_response": self.response_obj}

    fake_route_agent = MockAgent(AgentResponse(risk_score=2, recommended_action="Proceed", confidence=0.9, reasoning="All safe"))
    fake_cargo_agent = MockAgent(AgentResponse(risk_score=8, recommended_action="Stop", confidence=0.9, reasoning="High Temp"))
    fake_orch_agent = MockAgent(OrchestratorResponse(verdict="Halt immediately", action_plan=["Contact dispatch"], status="conclude", feedback="Agreed"))
    
    engine = DecisionEngine()
    engine.route_agent = fake_route_agent
    engine.cargo_agent = fake_cargo_agent
    engine.orchestrator_agent = fake_orch_agent
    
    context = [{"tick": 10, "trucks": []}]
    stream = engine.process_telemetry(context, tick=10)
    
    final_state = None
    for s in stream:
        final_state = s

    # Ensure final state has correct proposals
    assert final_state is not None
    assert final_state["verdict"]["status"] == "conclude"
    assert len(final_state["proposals"]) == 2
    
    route_prop = next(p for p in final_state["proposals"] if p["sender"] == "RouteAgent")
    assert route_prop["risk_score"] == 2
    
    cargo_prop = next(p for p in final_state["proposals"] if p["sender"] == "CargoAgent")
    assert cargo_prop["risk_score"] == 8
