import threading
import queue
import copy
from collections import deque

import solara

from mesa import Agent

from simulation.communication import ZeroMQTelemetryChannel
from config import (
    TELEMETRY_ENDPOINT,
    MONITORING_TOPIC,
    LLM_CALL_TIMEOUT_TICKS,
    TELEMETRY_PUBLISH_EVERY_TICKS,
)

from simulation.agents.decision_engine import DecisionEngine

# --- Mesa Simulation Integration ---

class OrchestratorAgent(Agent):
    """Integrates the LangGraph execution into the continuous Mesa simulation tick loop."""
    
    def __init__(self, model, output_channel):
        super().__init__(model)
        self.agent_name = f"orchestrator_{self.unique_id}"
        self.output_channel = output_channel
        
        # Initialize the LangGraph engine
        self.decision_engine = DecisionEngine()
        
        self._monitoring_subscriber = ZeroMQTelemetryChannel(
            endpoint=TELEMETRY_ENDPOINT,
            topic=MONITORING_TOPIC,
            bind=False,
        )
        self._recent_snapshots = deque(maxlen=3)
        self._last_received_tick = None
        self._last_analyzed_tick = None
        
        # Queue to offload LangGraph invocations so we don't stall the Mesa simulation
        self._analysis_queue = queue.Queue()
        self._worker_thread = threading.Thread(target=self._graph_executor_worker, daemon=True)
        self._worker_thread.start()

    def poll_monitoring_topic(self):
        """Consume monitoring telemetry snapshots into a local buffer."""
        while True:
            event = self._monitoring_subscriber.subscribe(block=False)
            if event is None:
                break
            if not isinstance(event, dict):
                continue
            
            payload = event.get("payload")
            payload_tick = event.get("tick")
            
            if isinstance(payload_tick, int):
                if self._last_received_tick is not None and payload_tick < self._last_received_tick:
                    self._recent_snapshots.clear()
                    self._last_analyzed_tick = None
                self._last_received_tick = payload_tick

            if isinstance(payload, list):
                # Store the entire list of truck snapshots for this tick together
                snapshot_group = {"tick": payload_tick, "trucks": payload}
                self._recent_snapshots.append(snapshot_group)
            self.model.latest_monitoring_payload = event

    def step(self):
        """Core simulation tick."""
        self.poll_monitoring_topic()
        current_tick = getattr(self.model, "tick", 0)
        
        # Trigger the LLM 3 ticks AFTER the regular telemetry publish interval
        # to ensure the buffer has the most up-to-date data.
        if current_tick < 3 or (current_tick - 3) % TELEMETRY_PUBLISH_EVERY_TICKS != 0:
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
        if len(history) < 3:
            return
            
        self._analysis_queue.put({"context": history, "tick": current_tick})
        self._last_analyzed_tick = current_tick

    def _graph_executor_worker(self):
        """Worker thread to invoke the compiled LangGraph without blocking simulation."""
        while True:
            try:
                task = self._analysis_queue.get()
                if task is None:
                    break
                
                # Use the abstracted DecisionEngine here to stream intermediate states
                state_stream = self.decision_engine.process_telemetry(
                    context=task["context"], 
                    tick=task["tick"]
                )
                
                final_state = None
                for current_state in state_stream:
                    # Save each interaction step for the UI dashboard
                    if not hasattr(self.model, "mas_history"):
                        self.model.mas_history = []
                    
                    # Deepcopy the state to ensure the UI captures the exact snapshot 
                    # before LangGraph mutates it in the next node
                    state_snapshot = copy.deepcopy(current_state)
                    
                    self.model.mas_history.append({"tick": task["tick"], "state": state_snapshot})
                    final_state = state_snapshot
                
                verdict = final_state.get("verdict") if final_state else None
                if verdict:
                    if self.output_channel:
                        self.output_channel.publish(
                            tick=task["tick"], 
                            source_agent=self.agent_name, 
                            payload=verdict
                        )
                    if not hasattr(self.model, "orchestrator_verdicts"):
                        self.model.orchestrator_verdicts = []
                    self.model.orchestrator_verdicts.append(verdict)
                    print(f"[Orchestrator Agent] Published verdict for tick {task['tick']}: {verdict}")
                    
            except Exception as e:
                print(f"Graph execution error: {e}")
            finally:
                self._analysis_queue.task_done()
