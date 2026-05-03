# FIGURE OUT WHY NEGOTIATION IS NOT WORKING

import json
import operator
from typing import TypedDict, Annotated, List, Dict, Any

from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent

from simulation.nodes import NODE_COORDINATES
from config import (
    ROUTE_ANALYSIS_AGENT_PROMPT,
    CARGO_SAFETY_AGENT_PROMPT,
    ORCHESTRATOR_AGENT_PROMPT,
    SIM_SCENARIOS,
)

class MASState(TypedDict):
    context: List[Dict[str, Any]]
    tick: int
    proposals: Annotated[List[Dict[str, Any]], operator.add]
    verdict: Dict[str, Any]
    iteration: int
    feedback: str

class DecisionEngine:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3.5:0.8b", temperature=0.0, streaming=True,
            base_url="http://192.168.144.153:11434", reasoning=False, top_p=0.95, top_k=64
        )
        self.route_system_prompt = f"{ROUTE_ANALYSIS_AGENT_PROMPT}\nNode coordinates: {NODE_COORDINATES}\nNormal route pattern is {SIM_SCENARIOS['normal']}\nRespond ONLY in valid rigid JSON format with keys: 'hypothesis', 'proposed_action', and 'risk_score' (1-10 severity)."
        self.cargo_system_prompt = f"{CARGO_SAFETY_AGENT_PROMPT}\nRespond ONLY in valid rigid JSON format with keys: 'hypothesis', 'proposed_action', and 'risk_score' (1-10 priority)."
        
        self.route_agent = create_agent(self.llm, system_prompt=self.route_system_prompt)
        self.cargo_agent = create_agent(self.llm, system_prompt=self.cargo_system_prompt)
        self.orchestrator_agent = create_agent(self.llm, system_prompt=ORCHESTRATOR_AGENT_PROMPT)
        self.graph = self._build_graph()

    def _format_prompt(self, state: MASState, agent_name: str) -> str:
        ctx_str = "Recent Telemetry:\n" + "".join(
            f"--- Tick {snap.get('tick')} ---\n" + "".join(
                f"  Truck {t.get('truck_id')}: {t.get('cargo_type')} | Pos: {t.get('position')} | Spd: {t.get('speed_kmh')} | Temp: {t.get('temperature_c')}C | CO2: {t.get('co2_ppm')}ppm\n"
                for t in snap.get("trucks", [])
            ) for snap in state["context"]
        )
        prompt = f"Analyze telemetry:\n{ctx_str}"
        
        # In a sequence, give agents context of what the Orchestrator wants them to rethink
        if state.get("feedback"):
            prompt += f"\n\nOrchestrator Feedback from previous iteration: {state['feedback']}\nPlease re-evaluate your stance."
            
        # Give the second agent in the sequence insight into what the first agent just proposed
        if agent_name == "CargoAgent":
            current_iter = state.get("iteration", 0)
            route_prop = next((p for p in state.get("proposals", []) if p["sender"] == "RouteAgent" and p["iteration"] == current_iter), None)
            if route_prop:
                prompt += f"\n\nNote: RouteAgent just proposed Risk Score {route_prop['risk_score']} based on: {route_prop['content'].get('hypothesis')}."
                
        return prompt

    def _agent_node(self, state: MASState, agent, sender_name: str):
        print(f"\n==================================================")
        print(f"[{sender_name}] Analyzing context for tick {state['tick']} (Iteration {state.get('iteration', 0)})...")
        
        try:
            response = agent.invoke({"messages": [HumanMessage(content=self._format_prompt(state, sender_name))]})
            # LangChain agents typically return the final state dict where 'messages' holds the trajectory
            raw_content = response["messages"][-1].content.replace('```json', '').replace('```', '').strip()
            result = json.loads(raw_content)
            
            print(f"[{sender_name}] Response:\n{json.dumps(result, indent=2)}")
            risk_score = int(result.get("risk_score", 0))
            print(f"[{sender_name}] ✅ Proposed action with Risk Score: {risk_score}")
            print(f"==================================================\n")
            return {"proposals": [{"sender": sender_name, "risk_score": risk_score, "iteration": state.get("iteration", 0), "content": {"hypothesis": result.get("hypothesis"), "action": result.get("proposed_action")}}]}
        except Exception as e: 
            print(f"[{sender_name}] Error parsing response: {e}")
            print(f"==================================================\n")
            return {"proposals": [{"sender": sender_name, "risk_score": 0, "iteration": state.get("iteration", 0), "content": {"hypothesis": "Error parsing response.", "action": "None"}}]}

    def _route_agent_node(self, state: MASState): return self._agent_node(state, self.route_agent, "RouteAgent")
    def _cargo_agent_node(self, state: MASState): return self._agent_node(state, self.cargo_agent, "CargoAgent")

    def _orchestrator_node(self, state: MASState):
        print(f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        current_iter = state.get("iteration", 0)
        print(f"[Orchestrator] Resolving conflicts in iteration {current_iter}...")
        proposals = [p for p in state.get("proposals", []) if p.get("iteration", 0) == current_iter]
        
        if not proposals: 
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "no_risk", "action_plan": "No proposals.", "highest_risk_score_agent": "None"}}
            
        highest_prop = max(proposals, key=lambda p: p["risk_score"])
        if highest_prop["risk_score"] == 0:
            print("[Orchestrator] All proposals have 0 risk. Finalizing.")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "no_risk", "action_plan": "Normal operations.", "highest_risk_score_agent": "None"}}

        prompt = (
            "You are the central orchestrator agent for freight fleet monitoring.\n"
            f"Note that '{highest_prop['sender']}' has a high risk_score ({highest_prop['risk_score']}).\n"
            "Please evaluate proposals. If agents strongly disagree, or if risk is high and they require alignment, return 'renegotiate' status.\n\nProposals:\n" + 
            "\n".join([f"[{p['sender']}] Risk Score: {p['risk_score']}, Content: {p['content']}" for p in proposals])
        )
        
        try:
            response = self.orchestrator_agent.invoke({"messages": [HumanMessage(content=prompt)]})
            raw_content = response["messages"][-1].content.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(raw_content)
            
            print(f"[Orchestrator] Response: {parsed}")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            
            if parsed.get("status") == "renegotiate" and current_iter < 2:
                return {"feedback": parsed.get("feedback", "Review each other's findings."), "iteration": current_iter + 1}
            else:
                return {"verdict": {
                    "verdict": parsed.get("verdict", "Unresolved Conflict"),
                    "action_plan": parsed.get("action_plan", "Manual review"),
                    "highest_risk_score_agent": highest_prop["sender"]
                }}
        except Exception as e:
            print(f"[Orchestrator] Error: {e}")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "Error", "action_plan": "Error parsing verdict.", "highest_risk_score_agent": highest_prop["sender"]}}

    def _should_continue(self, state: MASState):
        # 1. If Orchestrator explicitly chose 'renegotiate' (verdict was left empty)
        if state.get("verdict") is None:
            return "renegotiate"
            
        # 2. Or if forced to renegotiate because the final string is 'High Risk'
        verdict_dict = state.get("verdict")
        actual_verdict_str = verdict_dict.get("verdict", "")
        
        if actual_verdict_str in ["high_risk", "high risk", "High Risk"]:
            # Prevent infinite loops if High Risk can't be resolved after max iterations
            if state.get("iteration", 0) < 2:
                return "renegotiate"
                
        return "finalize"

    def _build_graph(self):
        builder = StateGraph(MASState)
        builder.add_node("RouteAgent", self._route_agent_node)
        builder.add_node("CargoAgent", self._cargo_agent_node)
        builder.add_node("Orchestrator", self._orchestrator_node)

        # Sequential sequence guarantees stable execution
        builder.add_edge(START, "RouteAgent")
        builder.add_edge("RouteAgent", "CargoAgent")
        builder.add_edge("CargoAgent", "Orchestrator")
        
        # Round-robin conditional sequence
        builder.add_conditional_edges("Orchestrator", self._should_continue, {
            "renegotiate": "RouteAgent", 
            "finalize": END
        })
        
        return builder.compile()

    def process_telemetry(self, context: List[Dict[str, Any]], tick: int) -> Dict[str, Any]:
        return self.graph.invoke({"context": context, "tick": tick, "proposals": [], "verdict": None, "iteration": 0, "feedback": ""})