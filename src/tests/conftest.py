import sys
import types
import queue
import importlib
import os
from typing import Optional
from unittest.mock import MagicMock
import pytest

# ──────────────────────────────────────────────
#  Minimal stubs so tests run without the full
#  project installed (no Mesa, ZMQ, LangChain).
# ──────────────────────────────────────────────

# ---------- ZeroMQ stub ----------
class _FakeSocket:
    def __init__(self, socket_type):
        self._type = socket_type
        self._q: queue.Queue = queue.Queue()
        self.closed = False
        self._sub_filter = ""

    def setsockopt(self, *a, **kw): pass
    def setsockopt_string(self, opt, val): self._sub_filter = val
    def bind(self, addr): pass
    def connect(self, addr): pass
    def close(self, linger=None): self.closed = True

    def send_multipart(self, parts):
        self._q.put(parts)

    def recv_multipart(self, flags=0):
        import zmq as _zmq
        block = (flags == 0)
        try:
            return self._q.get(block=block, timeout=0.05)
        except queue.Empty:
            raise _zmq.Again()


class _FakeZmqContext:
    PUB = 1; SUB = 2; LINGER = 3; SUBSCRIBE = 4; NOBLOCK = 5
    Again = type("Again", (Exception,), {})

    _shared: Optional["_FakeZmqContext"] = None

    @classmethod
    def instance(cls):
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    def socket(self, socket_type):
        return _FakeSocket(socket_type)

    def term(self): pass


# Patch zmq at import time before any project code is loaded.
_zmq_mod = types.ModuleType("zmq")
_zmq_mod.Context = _FakeZmqContext
_zmq_mod.PUB = _FakeZmqContext.PUB
_zmq_mod.SUB = _FakeZmqContext.SUB
_zmq_mod.LINGER = _FakeZmqContext.LINGER
_zmq_mod.SUBSCRIBE = _FakeZmqContext.SUBSCRIBE
_zmq_mod.NOBLOCK = _FakeZmqContext.NOBLOCK
_zmq_mod.EADDRINUSE = 98
_zmq_mod.Again = _FakeZmqContext.Again

class _FakeZMQError(Exception):
    def __init__(self, errno=0):
        self.errno = errno
_zmq_mod.ZMQError = _FakeZMQError

sys.modules["zmq"] = _zmq_mod


# ---------- Minimal config stub ----------
_config_mod = types.ModuleType("config")
_config_mod.MONITORING_TOPIC = "monitoring"
_config_mod.TELEMETRY_TOPIC = "telemetry"
_config_mod.TELEMETRY_ENDPOINT = "tcp://127.0.0.1:5555"
_config_mod.MONITORING_OUTPUT_DIR = "/tmp/sim_test_output"
_config_mod.ROUTE_ANALYSIS_TOPIC = "route_analysis"
_config_mod.CARGO_SAFETY_TOPIC = "cargo_safety"
_config_mod.ORCHESTRATOR_TOPIC = "orchestrator"
_config_mod.SIM_ACTIVE_SCENARIO = "normal"
_config_mod.SIM_NUM_TRUCKS = 2
_config_mod.SIM_SCENARIOS = {
    "normal": [["A", "B", "C"]],
    "anomaly_stop_open_at_d": [["A", "D", "C"]],
    "cargo_state": [["A", "B", "C"]],
}
_config_mod.SIM_SEED = 42
_config_mod.TELEMETRY_PUBLISH_EVERY_TICKS = 1
_config_mod.LLM_CALL_TIMEOUT_TICKS = 10
_config_mod.ROUTE_ANALYSIS_AGENT_PROMPT = "You are a route analysis agent."
_config_mod.CARGO_SAFETY_AGENT_PROMPT = "You are a cargo safety agent."
_config_mod.ORCHESTRATOR_AGENT_PROMPT = (
    "You are the orchestrator. Respond ONLY in valid JSON with keys: "
    "'verdict', 'action_plan', 'status', 'feedback'."
)
sys.modules["config"] = _config_mod

# ---------- Minimal mesa stubs ----------
class _FakeAgent:
    _next_id = 1
    def __init__(self, model):
        self.model = model
        self.unique_id = _FakeAgent._next_id
        _FakeAgent._next_id += 1

class _FakeModel:
    def __init__(self):
        self.agents: list = []
        self.tick = 0
        self.space = _FakeSpace()
        self.latest_monitoring_payload = None
        self.orchestrator_verdicts = []
        self.bad_truck_id = None

class _FakeSpace:
    def place_agent(self, agent, pos): pass
    def move_agent(self, agent, pos): pass

_mesa_mod = types.ModuleType("mesa")
_mesa_mod.Agent = _FakeAgent
_mesa_mod.Model = _FakeModel
sys.modules["mesa"] = _mesa_mod
sys.modules["mesa.space"] = types.ModuleType("mesa.space")
sys.modules["mesa.space"].ContinuousSpace = lambda **kw: _FakeSpace()

# ---------- LangChain / LangGraph stubs ----------
if not os.environ.get("RUN_INTEGRATION_TESTS"):
    for _m in [
        "langchain_google_genai",
        "langchain_ollama",
    ]:
        sys.modules.setdefault(_m, types.ModuleType(_m))

    # We leave langgraph and langchain.agents intact if we can, or just mock what we need.
    import langgraph.graph
    class _FakeStateGraph:
        def __init__(self, schema, *args, **kw): self._nodes = {}; self._edges = []; self._cond = {}
        def add_node(self, name, fn): self._nodes[name] = fn
        def add_edge(self, a, b): self._edges.append((a, b))
        def add_conditional_edges(self, src, fn, mapping): self._cond[src] = (fn, mapping)
        def compile(self, *args, **kw): return self

        def invoke(self, state):
            state = dict(state)
            state = {**state, **self._nodes["RouteAgent"](state)}
            state = {**state, **self._nodes["CargoAgent"](state)}
            state = {**state, **self._nodes["Orchestrator"](state)}
            return state

        def stream(self, state, *args, **kw):
            mock_state = self.invoke(state)
            yield mock_state

    langgraph.graph.StateGraph = _FakeStateGraph

# Only mock real LLMs if we aren't explicitly running integration tests
if not os.environ.get("RUN_INTEGRATION_TESTS"):
    sys.modules["langchain_google_genai"].ChatGoogleGenerativeAI = MagicMock
    sys.modules["langchain_ollama"].ChatOllama = MagicMock

# Mark dotenv as no-op
_dotenv = types.ModuleType("dotenv")
_dotenv.load_dotenv = lambda: None
sys.modules["dotenv"] = _dotenv

# Communication layer setup
sys.path.insert(0, "/mnt/user-data/uploads")
_base = "/mnt/user-data/uploads"

def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, f"{_base}/{filename}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except FileNotFoundError:
        pass # Handled by the fact we're inside the repo now
    return mod

# For our local tests, we don't really need the upload logic since the files are right there in `src/`.
# Let's fix this for the new test structure:

import simulation.communication
import simulation.nodes
import simulation.schemas

# Fixtures

@pytest.fixture
def normal_truck_snapshot():
    def _snapshot(truck_id="1", tick=10):
        return {
            "truck_id": truck_id,
            "cargo_type": "Electronics",
            "position": [50.0, 0.0],
            "speed_kmh": 80.0,
            "temperature_c": 20.0,
            "co2_ppm": 250.0,
            "door_open": False,
        }
    return _snapshot

@pytest.fixture
def anomaly_truck_snapshot(normal_truck_snapshot):
    def _snapshot(truck_id="1", tick=10, door_open=True, speed=0.0, temp=38.0, co2=900.0):
        snap = normal_truck_snapshot(truck_id, tick)
        snap.update({"door_open": door_open, "speed_kmh": speed, "temperature_c": temp, "co2_ppm": co2})
        return snap
    return _snapshot

@pytest.fixture
def make_context(normal_truck_snapshot, anomaly_truck_snapshot):
    def _make(snapshots_per_tick=None, ticks=(5, 10, 15)):
        if snapshots_per_tick is None:
            snapshots_per_tick = [[normal_truck_snapshot("1", t), normal_truck_snapshot("2", t)] for t in ticks]
        return [{"tick": t, "trucks": s} for t, s in zip(ticks, snapshots_per_tick)]
    return _make

@pytest.fixture
def fake_socket_class():
    return _FakeSocket
