import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from config import TELEMETRY_ENDPOINT, TELEMETRY_TOPIC
from simulation.schemas import TRUCK_TELEMETRY_SCHEMA
import zmq


_publisher_lock = threading.Lock()
_shared_publishers = {}


class ZeroMQTelemetryChannel:
	"""Ephemeral ZeroMQ pub/sub channel for truck telemetry events."""

	def __init__(
		self,
		*,
		endpoint=TELEMETRY_ENDPOINT,
		topic=TELEMETRY_TOPIC,
		schema=TRUCK_TELEMETRY_SCHEMA,
	):
		self.topic = topic
		self.endpoint = endpoint
		self.schema = schema
		self.message_id_counters = {}

		with _publisher_lock:
			shared = _shared_publishers.get(self.endpoint)
			if shared and not shared["publisher"].closed:
				self.context = shared["context"]
				self._publisher = shared["publisher"]
				shared["ref_count"] += 1
				self._owns_socket = False
				return

			self.context = zmq.Context.instance()
			self._publisher = self.context.socket(zmq.PUB)
			self._publisher.setsockopt(zmq.LINGER, 0)

			# Normal path: this channel owns the bound publisher.
			# If already bound externally, fall back to connect so app reset does not crash.
			self._owns_socket = True
			try:
				self._publisher.bind(self.endpoint)
			except zmq.ZMQError as err:
				if err.errno == zmq.EADDRINUSE:
					self._publisher.connect(self.endpoint)
					self._owns_socket = False
				else:
					self._publisher.close(linger=0)
					raise

			_shared_publishers[self.endpoint] = {
				"context": self.context,
				"publisher": self._publisher,
				"ref_count": 1,
			}

	def publish(self, *, tick, source_agent, payload):
		"""Publish a telemetry event to subscribers.

		Events are not stored in memory by this channel.
		"""
		# message id not shared anymore
		truck_key = str(payload.get("truck_id", source_agent))
		message_id = self.message_id_counters.get(truck_key, 0)
		self.message_id_counters[truck_key] = message_id + 1

		event = {
			"schema": self.schema,
			"message_id": message_id,
			"timestamp_utc": datetime.now(timezone.utc).isoformat(),
			"tick": tick,
			"source_agent": source_agent,
			"payload": payload,
		}

		self._publisher.send_multipart(
			[self.topic.encode("utf-8"), json.dumps(event).encode("utf-8")]
		)
		return event

	def close(self):
		with _publisher_lock:
			shared = _shared_publishers.get(self.endpoint)
			if not shared:
				return

			shared["ref_count"] -= 1
			if shared["ref_count"] > 0:
				return

			publisher = shared["publisher"]
			if not publisher.closed:
				publisher.close(linger=0)

			# If this process used Context.instance(), do not terminate it here.
			_shared_publishers.pop(self.endpoint, None)


def run_telemetry_subscriber(endpoint, topic, output_root):
	"""Subscribe to a topic and append each event as a JSON line."""
	output_base = Path(output_root)
	output_base.mkdir(parents=True, exist_ok=True)
	log_file = output_base / "output.json"

	# Start each subscriber run with a clean output file.
	with log_file.open("w", encoding="utf-8"):
		pass

	context = zmq.Context()
	subscriber = context.socket(zmq.SUB)
	subscriber.connect(endpoint)
	subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

	try:
		last_tick = None
		while True:
			_ignored_topic, raw_payload = subscriber.recv_multipart()
			event = json.loads(raw_payload.decode("utf-8"))

			# If tick goes backwards, a new simulation run started: clear old logs.
			event_tick = event.get("tick")
			if isinstance(event_tick, int):
				if last_tick is not None and event_tick < last_tick:
					with log_file.open("w", encoding="utf-8"):
						pass
				last_tick = event_tick

			with log_file.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event))
				handle.write("\n")
	finally:
		subscriber.close(linger=0)
		context.term()
