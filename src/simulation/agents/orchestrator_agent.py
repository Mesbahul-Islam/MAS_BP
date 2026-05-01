import json
import threading
import queue
from collections import deque

from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from langchain.tools import tool
from mesa import Agent

from simulation.communication import ZeroMQTelemetryChannel
from simulation.nodes import NODE_COORDINATES
from config import (
    TELEMETRY_ENDPOINT,
    MONITORING_TOPIC,
    ORCHESTRATOR_TOPIC,
    ROUTE_ANALYSIS_AGENT_PROMPT,
    CARGO_SAFETY_AGENT_PROMPT,
    ORCHESTRATOR_AGENT_PROMPT,
    LLM_CALL_TIMEOUT_TICKS,
    SIM_SCENARIOS,
    TELEMETRY_PUBLISH_EVERY_TICKS,
)

# 1. Setup the shared LLM
_llm = ChatOllama(
    model="granite4.1:3b",
    temperature=0,
    max_tokens=5120,
    streaming=True,
    base_url="http://192.168.144.153:11434",
)

# 2. Create the specialized sub-agents
route_agent = create_agent(
    model=_llm,
    system_prompt=SystemMessage(content=[
        {"type": "text", "text": ROUTE_ANALYSIS_AGENT_PROMPT},
        {"type": "text", "text": f"Node coordinates: {NODE_COORDINATES}"},
        {"type": "text", "text": f"Normal route pattern is {SIM_SCENARIOS['normal']}"}
    ])
)

cargo_agent = create_agent(
    model=_llm,
    system_prompt=SystemMessage(content=[
        {"type": "text", "text": CARGO_SAFETY_AGENT_PROMPT}
    ])
)

# 3. Wrap sub-agents as tools
@tool
def analyze_route(context: str) -> str:
    """Analyze the route and movement of the truck given the telemetry context snapshot.
    Returns a hypothesis about any route anomalies."""
    print(f"\n[Route Analysis Sub-Agent] 🔍 Invoked with context length: {len(context)}")
    result = route_agent.invoke({
        "messages": [HumanMessage(content=f"Analyze this telemetry context for route anomalies: {context}")]
    })
    output = result["messages"][-1].content
    print(f"[Route Analysis Sub-Agent] ✅ Result: {output[:150]}...")
    return output

@tool
def analyze_cargo(context: str) -> str:
    """Analyze the cargo safety of the truck (temperature, CO2) given the telemetry context snapshot.
    Returns a hypothesis about any cargo anomalies."""
    print(f"\n[Cargo Safety Sub-Agent] 🔍 Invoked with context length: {len(context)}")
    result = cargo_agent.invoke({
        "messages": [HumanMessage(content=f"Analyze this telemetry context for cargo safety anomalies: {context}")]
    })
    output = result["messages"][-1].content
    print(f"[Cargo Safety Sub-Agent] ✅ Result: {output[:150]}...")
    return output

class OrchestratorAgent(Agent):
    """Central supervisor agent that orchestrates Route Analysis and Cargo Safety
    using the LangChain Supervisor pattern."""

    def __init__(self, model, output_channel):
        super().__init__(model)
        self.agent_name = f"orchestrator_{self.unique_id}"
        self.output_channel = output_channel
        
        # 4. Create Supervisor
        self.supervisor_agent = create_agent(
            model=_llm,
            tools=[analyze_route, analyze_cargo],
            system_prompt=SystemMessage(content=ORCHESTRATOR_AGENT_PROMPT)
        )

        self._monitoring_subscriber = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MONITORING_TOPIC,
            bind=False,
        )

        self._recent_snapshots = deque(maxlen=3)
        self._last_received_tick = None
        self._last_analyzed_tick = None
        
        self._analysis_queue = queue.Queue(maxsize=1)
        self._worker_thread = threading.Thread(target=self.analysis_worker, daemon=True)
        self._worker_thread.start()

    def poll_monitoring_topic(self):
        """Consume monitoring telemetry snapshots."""
        while True:
            event = self._monitoring_subscriber.subscribe(block=False)
            if event is None:
                break
            if not isinstance(event, dict):
                continue
            payload = event.get("payload")
            if not isinstance(payload, list):
                continue

            payload_tick = event.get("tick")
            if isinstance(payload_tick, int):
                if self._last_received_tick is not None and payload_tick < self._last_received_tick:
                    self._recent_snapshots.clear()
                    self._last_analyzed_tick = None
                    while not self._analysis_queue.empty():
                        try:
                            self._analysis_queue.get_nowait()
                        except queue.Empty:
                            break
                self._last_received_tick = payload_tick

            for snapshot in payload:
                if isinstance(snapshot, dict):
                    self._recent_snapshots.append(snapshot)
            self.model.latest_monitoring_payload = event

    def step(self):
        """Core simulation tick."""
        self.poll_monitoring_topic()
        current_tick = getattr(self.model, "tick", 0)
        
        if current_tick % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
            return

        monitoring_event = getattr(self.model, "latest_monitoring_payload", None)
        if not monitoring_event:
            return
        
        payload_tick = monitoring_event.get("tick", current_tick)
        
        if self._last_analyzed_tick is not None and current_tick - self._last_analyzed_tick < LLM_CALL_TIMEOUT_TICKS:
            return
        if self._last_analyzed_tick == payload_tick:
            return
            
        history = list(self._recent_snapshots)[-3:]
        if not history:
            return
            
        context_str = json.dumps(history, ensure_ascii=True)
        try:
            self._analysis_queue.put_nowait((context_str, current_tick))
        except queue.Full:
            pass 

        self._last_analyzed_tick = current_tick

    def analysis_worker(self):
        """Worker thread for orchestrator LLM to prevent blocking simulation"""
        while True:
            try:
                item = self._analysis_queue.get()
                if item is None:
                    break
                
                snapshot_context, tick = item
                verdict = self.fetch_supervisor_verdict(snapshot_context)
                
                if verdict:
                    if self.output_channel:
                        self.output_channel.publish(
                            tick=tick, 
                            source_agent=self.agent_name, 
                            payload=verdict
                        )
                    if not hasattr(self.model, "orchestrator_verdicts"):
                        self.model.orchestrator_verdicts = []
                    self.model.orchestrator_verdicts.append(verdict)
                    
            except Exception as e:
                print(f"Orchestrator worker error: {e}")
            finally:
                self._analysis_queue.task_done()

    def fetch_supervisor_verdict(self, snapshot_context):
        print(f"\n[Supervisor Agent] 🧠 Analyzing new context snapshot (length {len(snapshot_context)})")
        message_obj = HumanMessage(
            "Review the latest telemetry snapshots. "
            "Use the `analyze_route` and `analyze_cargo` tools to evaluate the situation. "
            "Then, based on their output, provide the final combined verdict and prescription explicitly. "
            "Return JSON with only: {\"verdict\": \"...\", \"action_plan\": \"...\"}. "
            f"context: {snapshot_context}"
        )
        try:
            response = self.supervisor_agent.invoke({"messages": [message_obj]})
            content = response['messages'][-1].content
            print(f"\n[Supervisor Agent] 🎯 Final Response: {content}")
            
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "verdict" in parsed:
                return {
                    "verdict": parsed.get("verdict", ""),
                    "action_plan": parsed.get("action_plan", ""),
                }
        except json.JSONDecodeError:
            print("Failed to decode JSON from Supervisor LLM response.")
        except Exception as e:
            print(f"Supervisor Model Error: {e}")
        return None