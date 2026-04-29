import json
import threading
import queue
from collections import deque

from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from mesa import Agent

from simulation.nodes import NODE_COORDINATES
from simulation.communication import ZeroMQTelemetryChannel
from config import (
    MONITORING_TOPIC,
    TELEMETRY_ENDPOINT,
    TELEMETRY_PUBLISH_EVERY_TICKS,
    SIM_SCENARIOS,
    ROUTE_ANALYSIS_AGENT_PROMPT,
    LLM_CALL_TIMEOUT_TICKS,
)


class RouteAnalysisAgent(Agent):
    """Analyzes route telemetry using an LLM running in a background thread
    """

    def __init__(self, model):
        super().__init__(model)
        self.agent_name = f"route_analysis_{self.unique_id}"
        
        # system prompt for ai agents
        self.prompt = SystemMessage(
            content=[
                {"type": "text", "text": ROUTE_ANALYSIS_AGENT_PROMPT},
                {"type": "text", "text": f"Node coordinates: {NODE_COORDINATES}"},
                {"type": "text", "text": f"Normal route pattern is {SIM_SCENARIOS['normal']}"}
            ]
        )

        # handle telemetry subscription
        self._monitoring_subscriber = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MONITORING_TOPIC,
            bind=False,
        )

        self._recent_snapshots = deque(maxlen=3)
        self._last_received_tick = None
        self._last_analyzed_tick = None

        #llm setup
        self.llm = ChatOpenRouter(
            model="poolside/laguna-m.1:free",
            temperature=0,
            max_tokens=5120,
            streaming=True,
        )
        self.llm_agent = create_agent(model=self.llm, system_prompt=self.prompt)

        #spawn threads
        self._analysis_queue = queue.Queue(maxsize=1) # Limit to 1 to never stack up outdated tasks
        self._worker_thread = threading.Thread(target=self.analysis_worker, daemon=True)
        self._worker_thread.start()

    def poll_monitoring_topic(self):
        """Drain queued monitoring events and update rolling windows without blocking."""
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

            # Simulation restarted (tick goes backward): clear old cached data.
            if isinstance(payload_tick, int):
                if self._last_received_tick is not None and payload_tick < self._last_received_tick:
                    self._recent_snapshots.clear()
                    self._last_analyzed_tick = None
                    
                    # Flush the queue to prevent analyzing outdated hypotheses
                    while not self._analysis_queue.empty():
                        try:
                            self._analysis_queue.get_nowait()
                        except queue.Empty:
                            break

                self._last_received_tick = payload_tick

            for snapshot in payload:
                if isinstance(snapshot, dict):
                    self._recent_snapshots.append(snapshot)

            # Keep model up to date
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
        
        # Cooldown period check
        if self._last_analyzed_tick is not None and current_tick - self._last_analyzed_tick < LLM_CALL_TIMEOUT_TICKS:
            return

        if self._last_analyzed_tick == payload_tick:
            return

        # If we have new data and are out of cooldown, queue it for analysis
        if not hasattr(self.model, "route_analysis_hypotheses"):
            self.model.route_analysis_hypotheses = []
        
        payload_entries = monitoring_event.get("payload")
        if not isinstance(payload_entries, list):
            return
            
        for snapshot in payload_entries:
            if isinstance(snapshot, dict):
                self.queue_snapshot_for_analysis(snapshot)

        self._last_analyzed_tick = current_tick

    def queue_snapshot_for_analysis(self, snapshot):
        """Packages recent snapshots and sends them to the worker queue."""
        history = list(self._recent_snapshots)[-3:]
        if not history:
            history = [snapshot]

        context_str = json.dumps(history, ensure_ascii=True)
        #If the queue is full (LLM is busy), gracefully drop the frame
        try:
            self._analysis_queue.put_nowait(context_str)
        except queue.Full:
            pass 

    def analysis_worker(self):
        """Background thread that consumes the queue one by one."""
        while True:
            try:
                snapshot_context = self._analysis_queue.get()
                if snapshot_context is None:
                    break
                    
                hypothesis = self.fetch_llm_hypothesis(snapshot_context)
                if hypothesis:
                    # Thread-safe enough appending operation for Mesa models
                    self.model.route_analysis_hypotheses.append(hypothesis)
            except Exception as e:
                print(f"Analysis worker error: {e}")
            finally:
                self._analysis_queue.task_done()

    def fetch_llm_hypothesis(self, snapshot_context):
        """Generates a hypothesis output and safely parses JSON."""


        message_obj = HumanMessage(
            "Analyze the latest telemetry with the last 3 snapshots context. "
            "Return JSON with only: {\"hypothesis\": \"...\", "
            "\"confidence\": 0.0, \"evidence\": \"...\"}. "
            f"context: {snapshot_context}"
        )
    
        try:
            response = self.llm_agent.invoke({"messages": [message_obj]})
            content = response['messages'][-1].content
            print(f"LLM response: {content}")
            
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "hypothesis" in parsed:
                return {
                    "hypothesis": parsed.get("hypothesis", ""),
                    "confidence": float(parsed.get("confidence", 0.0)),
                    "evidence": parsed.get("evidence", ""),
                }
        except json.JSONDecodeError:
            print("Failed to decode JSON from LLM response.")
        except Exception as e:
            print(f"Model Error: {e}")
        return None