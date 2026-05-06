# FIGURE OUT WHY NEGOTIATION IS NOT WORKING

import operator
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from simulation.nodes import NODE_COORDINATES
from config import (
    ROUTE_ANALYSIS_AGENT_PROMPT,
    CARGO_SAFETY_AGENT_PROMPT,
    ORCHESTRATOR_AGENT_PROMPT,
    SIM_SCENARIOS,
)

# --- LangGraph State Definition ---

class MASState(TypedDict):
    """
    Holds the execution state as it propagates through the LangGraph nodes.
    Each agent reads and modifies this state.
    """
    context: List[Dict[str, Any]]                # Telemetry snapshots being analyzed
    tick: int                                    # Current simulation tick
    proposals: Annotated[List[Dict[str, Any]], operator.add] # Agent verdicts (accumulates)
    verdict: Dict[str, Any]                      # Final decision dictionary from the Orchestrator
    iteration: int                               # Negotiation round counter (0, 1, 2...)
    feedback: str                                # Orchestrator feedback used to steer renegotiation

# --- Pydantic Schemas for Structured LLM Outputs ---

class AgentResponse(BaseModel):
    """Structured output expected from the Route and Cargo agents."""
    hypothesis: str = Field(description="Explanation of what is happening based on telemetry.")
    proposed_action: str = Field(description="The action the system should take.")
    risk_score: int = Field(description="Numeric risk level from 1 to 10.", ge=0, le=10)

class OrchestratorResponse(BaseModel):
    """Structured output expected from the Orchestrator agent."""
    status: Literal["conclude", "renegotiate"] = Field(description="Action outcome status.")
    verdict: str = Field(description="The final risk assessment, e.g., 'High Risk' or 'no_risk'.")
    action_plan: str = Field(description="Detailed plan of action for the fleet.")
    feedback: str = Field(default="", description="Feedback instructions for the agents if status is 'renegotiate'.")

# --- Core Multi-Agent Graph Engine ---

class DecisionEngine:
    """
    Manages the LangGraph orchestration of three LLM agents:
    1. Route Agent: Evaluates navigation and positional anomalies.
    2. Cargo Agent: Evaluates environmental and payload metrics.
    3. Orchestrator: Acts as the judge, resolving conflicts and forcing renegotiation if necessary.
    """
    def __init__(self, llm=None):
        # Initialize the base LLM model
        if llm is None:
            from config import GOOGLE_API_KEY, GOOGLE_MODEL

            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is not set. Add it to your environment or .env file.")

            self.llm = ChatGoogleGenerativeAI(
                model=GOOGLE_MODEL,
                temperature=0.5,
                google_api_key=GOOGLE_API_KEY,
                convert_system_message_to_human=True,
            )
        else:
            self.llm = llm
        
        # Build individual system prompts
        self.route_system_prompt = f"{ROUTE_ANALYSIS_AGENT_PROMPT}\nNode coordinates: {NODE_COORDINATES}\nNormal route pattern is {SIM_SCENARIOS['normal']}"
        self.cargo_system_prompt = f"{CARGO_SAFETY_AGENT_PROMPT}"
        
        # Instantiate the agents, binding them to Pydantic structured output models
        self.route_agent = create_agent(self.llm, system_prompt=self.route_system_prompt, response_format=AgentResponse)
        self.cargo_agent = create_agent(self.llm, system_prompt=self.cargo_system_prompt, response_format=AgentResponse)
        self.orchestrator_agent = create_agent(self.llm, system_prompt=ORCHESTRATOR_AGENT_PROMPT, response_format=OrchestratorResponse)
        
        # Compile the state graph representing the execution loop
        self.graph = self._build_graph()

    def _format_prompt(self, state: MASState, agent_name: str) -> str:
        """
        Constructs the textual prompt payload for an agent based on recent telemetry.
        Injects context like orchestrator feedback or peers' recent proposals.
        """
        ctx_str = "Recent Telemetry:\n" + "".join(
            f"--- Tick {snap.get('tick')} ---\n" + "".join(
                f"  Truck {t.get('truck_id')}: {t.get('cargo_type')} | Pos: {t.get('position')} | Spd: {t.get('speed_kmh')} | Temp: {t.get('temperature_c')}C | CO2: {t.get('co2_ppm')}ppm\n"
                for t in snap.get("trucks", [])
            ) for snap in state["context"]
        )
        prompt = f"Analyze telemetry:\n{ctx_str}"
        
        # If the Orchestrator triggered a renegotiation loop, inject its feedback into the prompt
        if state.get("feedback"):
            prompt += f"\n\nOrchestrator Feedback from previous iteration: {state['feedback']}\nPlease re-evaluate your stance."
            
        # Give the CargoAgent (the second node in the sequence) insight into what the RouteAgent just proposed
        if agent_name == "CargoAgent":
            current_iter = state.get("iteration", 0)
            route_prop = next((p for p in state.get("proposals", []) if p["sender"] == "RouteAgent" and p["iteration"] == current_iter), None)
            if route_prop:
                prompt += f"\n\nNote: RouteAgent just proposed Risk Score {route_prop['risk_score']} based on: {route_prop['content'].get('hypothesis')}."
                
        return prompt

    def _agent_node(self, state: MASState, agent, sender_name: str):
        """
        Generic LangGraph node execution function used by both Route and Cargo agents.
        Appends the generated structured response to the State's list of proposals.
        """
        print(f"\n==================================================")
        print(f"[{sender_name}] Analyzing context for tick {state['tick']} (Iteration {state.get('iteration', 0)})...")
        
        try:
            response = agent.invoke({"messages": [HumanMessage(content=self._format_prompt(state, sender_name))]})
            
            structured_data = response.get("structured_response")
            
            print(f"[{sender_name}] Response:\n{structured_data}")
            risk_score = structured_data.risk_score
            print(f"[{sender_name}] Proposed action with Risk Score: {risk_score}")
            print(f"==================================================\n")
            
            # Map the parsed Pydantic data back into a serializable dictionary for State storage
            proposal = {
                "sender": sender_name, 
                "risk_score": risk_score, 
                "iteration": state.get("iteration", 0), 
                "content": {
                    "hypothesis": structured_data.hypothesis, 
                    "action": structured_data.proposed_action
                }
            }
            return {"proposals": [proposal]}
            
        except Exception as e: 
            # Fallback logic to prevent Graph crashes if the model drops the structure
            print(f"[{sender_name}] Error processing structured output response: {e}")
            print(f"==================================================\n")
            return {"proposals": [{"sender": sender_name, "risk_score": 0, "iteration": state.get("iteration", 0), "content": {"hypothesis": "Error parsing fallback.", "action": "None"}}]}

    def _route_agent_node(self, state: MASState): 
        return self._agent_node(state, self.route_agent, "RouteAgent")
        
    def _cargo_agent_node(self, state: MASState): 
        return self._agent_node(state, self.cargo_agent, "CargoAgent")

    def _orchestrator_node(self, state: MASState):
        """
        LangGraph node executing the Orchestrator. 
        It evaluates the recent proposals from Cargo and Route.
        """
        print(f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        current_iter = state.get("iteration", 0)
        print(f"[Orchestrator] Resolving conflicts in iteration {current_iter}...")
        
        # Only look at proposals generated in the current Round-Robin iteration cycle
        proposals = [p for p in state.get("proposals", []) if p.get("iteration", 0) == current_iter]
        
        # Edge case: Missing proposals
        if not proposals: 
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "no_risk", "action_plan": "No proposals.", "highest_risk_score_agent": "None"}}
            
        highest_prop = max(proposals, key=lambda p: p["risk_score"])
        
        # Early exit: If the maximum risk score is 0, we don't even need to query the Orchestrator
        if highest_prop["risk_score"] == 0:
            print("[Orchestrator] All proposals have 0 risk. Finalizing.")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "no_risk", "action_plan": "Normal operations.", "highest_risk_score_agent": "None"}}

        prompt = (
            "You are the central orchestrator agent for freight fleet monitoring.\n"
            f"Note that '{highest_prop['sender']}' has a high risk_score ({highest_prop['risk_score']}).\n"
            "After you are done evaluating the proposals, present a 5 point action plan if you conclude there is a risk\n"
            "Please evaluate proposals. If agents strongly disagree, or if risk is high and they require alignment, return 'renegotiate' status.\n\nProposals:\n" + 
            "\n".join([f"[{p['sender']}] Risk Score: {p['risk_score']}, Content: {p['content']}" for p in proposals])
        )
        
        try:
            response = self.orchestrator_agent.invoke({"messages": [HumanMessage(content=prompt)]})
            structured_data = response.get("structured_response")
            
            print(f"[Orchestrator] Response: {structured_data}")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            
            status = structured_data.status
            verdict_str = structured_data.verdict
            
            # Failsafe: Enforce a renegotiation round if the Orchestrator flagged an issue as High Risk 
            # but accidentally specified status="conclude". This forces the agents to double-check a severe anomaly.
            if status != "renegotiate" and verdict_str in ["high_risk", "high risk", "High Risk"]:
                status = "renegotiate"
                structured_data.feedback = "High Risk detected. Please do a secondary verification to confirm the anomaly."
            
            # Trigger Renegotiation Loop
            if status == "renegotiate" and current_iter < 2:
                # To renegotiate: update iteration count, pass feedback, and leave 'verdict' empty.
                return {
                    "feedback": getattr(structured_data, "feedback", "Review each other's findings."), 
                    "iteration": current_iter + 1,
                    "verdict": None  # Setting verdict to None signals _should_continue to restart the loop
                }
            # Finalize Process
            else:
                return {"verdict": {
                    "verdict": verdict_str,
                    "action_plan": structured_data.action_plan,
                    "highest_risk_score_agent": highest_prop["sender"]
                }}
        except Exception as e:
            print(f"[Orchestrator] Error: {e}")
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            return {"verdict": {"verdict": "Error", "action_plan": "Error parsing verdict.", "highest_risk_score_agent": highest_prop["sender"]}}

    def _should_continue(self, state: MASState):
        """
        LangGraph Conditional Edge router. Executed immediately after the Orchestrator node.
        """
        # If the Orchestrator node yielded no verdict, it indicates a renegotiation sequence
        # was activated, so we route the edge back to the beginning of the chain (RouteAgent).
        if state.get("verdict") is None:
            return "renegotiate"
            
        # Graph execution reached an end condition
        return "finalize"

    def _build_graph(self):
        """Builds and compiles the underlying LangGraph state machine."""
        builder = StateGraph(MASState)
        
        builder.add_node("RouteAgent", self._route_agent_node)
        builder.add_node("CargoAgent", self._cargo_agent_node)
        builder.add_node("Orchestrator", self._orchestrator_node)

        # Sequential flow allows downstream agents to read upstream proposals
        builder.add_edge(START, "RouteAgent")
        builder.add_edge("RouteAgent", "CargoAgent")
        builder.add_edge("CargoAgent", "Orchestrator")
        
        # Conditional dynamic routing
        builder.add_conditional_edges("Orchestrator", self._should_continue, {
            "renegotiate": "RouteAgent", 
            "finalize": END
        })
        memory = InMemorySaver()
        return builder.compile(checkpointer=memory)

    def process_telemetry(self, context: List[Dict[str, Any]], tick: int):
        """
        Entry point to process a new chunk of telemetry. 
        Returns a stream generator to track intermediate steps.
        """

        config = {"configurable": {"thread_id": "simulation_run_1"}}
        # Initialize clean state. Agent states accumulate in the 'proposals' array over iter loops.
        initial_state = {
            "context": context, 
            "tick": tick, 
            "proposals": [], 
            "verdict": None, 
            "iteration": 0, 
            "feedback": ""
        }
        # Yield the state after every node executes
        return self.graph.stream(initial_state, config=config, stream_mode="values")