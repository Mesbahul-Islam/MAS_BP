import json
import threading
from datetime import datetime, timezone
from pathlib import Path

import zmq


_publisher_lock = threading.Lock()
_shared_publishers = {}


class ZeroMQTelemetryChannel:
	"""Ephemeral ZeroMQ pub/sub channel for truck telemetry events."""

	def __init__(
		self,
		*,
		endpoint,
		topic,
		schema=None,
		bind=True,
	):
		self.topic = topic
		self.endpoint = endpoint
		self.schema = schema
		self.message_id_counters = {}
		self._bind = bind
		self._publisher_initialized = False
		self._subscriber = None

	def _ensure_publisher(self):
		if self._publisher_initialized:
			return

		with _publisher_lock:
			shared = _shared_publishers.get(self.endpoint)
			if shared and not shared["publisher"].closed:
				self.context = shared["context"]
				self._publisher = shared["publisher"]
				shared["ref_count"] += 1
				self._publisher_initialized = True
				return

			self.context = zmq.Context.instance()
			self._publisher = self.context.socket(zmq.PUB)
			self._publisher.setsockopt(zmq.LINGER, 0)

			# Default behavior is to bind (server). If already bound, fall back to connect.
			try:
				if self._bind:
					self._publisher.bind(self.endpoint)
				else:
					self._publisher.connect(self.endpoint)
			except zmq.ZMQError as err:
				if self._bind and err.errno == zmq.EADDRINUSE:
					self._publisher.connect(self.endpoint)
				else:
					self._publisher.close(linger=0)
					raise

			_shared_publishers[self.endpoint] = {
				"context": self.context,
				"publisher": self._publisher,
				"ref_count": 1,
			}
			self._publisher_initialized = True

	def _ensure_subscriber(self):
		if self._subscriber is not None:
			return
		context = zmq.Context.instance()
		self._subscriber = context.socket(zmq.SUB)
		self._subscriber.setsockopt(zmq.LINGER, 0)
		self._subscriber.connect(self.endpoint)
		self._subscriber.setsockopt_string(zmq.SUBSCRIBE, self.topic)

	def publish(self, *, tick, source_agent, payload):
		"""Publish a telemetry event to subscribers.

		Events are not stored in memory by this channel.
		"""
		self._ensure_publisher()

		# message id not shared anymore
		if isinstance(payload, dict):
			truck_key = str(payload.get("truck_id", source_agent))
		else:
			truck_key = str(source_agent)
		message_id = self.message_id_counters.get(truck_key, 0)
		self.message_id_counters[truck_key] = message_id + 1

		event = {
			"tick": tick,
			"message_id": message_id,
			"timestamp_utc": datetime.now(timezone.utc).isoformat(),
			"source_agent": source_agent,
			"payload": payload,
		}

		self._publisher.send_multipart(
			[self.topic.encode("utf-8"), json.dumps(event).encode("utf-8")]
		)
		return event

	def subscribe(self, *, block=True):
		"""Receive the next event for this channel.

		If block=False and no message is available, returns None.
		"""
		self._ensure_subscriber()
		flags = 0 if block else zmq.NOBLOCK
		try:
			_ignored_topic, raw_payload = self._subscriber.recv_multipart(flags=flags)
		except zmq.Again:
			return None
		try:
			return json.loads(raw_payload.decode("utf-8"))
		except json.JSONDecodeError:
			return None

	def close(self):
		if self._subscriber is not None and not self._subscriber.closed:
			self._subscriber.close(linger=0)
			self._subscriber = None

		if not self._publisher_initialized:
			return

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
			self._publisher_initialized = False


def run_telemetry_subscriber(endpoint, topic, output_root):
	"""Subscribe to a topic and append each event as a JSON line."""
	output_base = Path(output_root)
	output_base.mkdir(parents=True, exist_ok=True)
	log_file = output_base / "output.jsonl"

	# Start each subscriber run with a clean output file.
	with log_file.open("w", encoding="utf-8"):
		pass

	channel = ZeroMQTelemetryChannel(endpoint=endpoint, topic=topic)
	try:
		last_tick = None
		while True:
			event = channel.subscribe(block=True)
			if event is None:
				continue

			# If tick goes backwards, a new simulation run started: clear old logs.
			event_tick = event.get("tick")
			if not isinstance(event_tick, int):
				payload = event.get("payload")
				payload_tick = payload.get("tick") if isinstance(payload, dict) else None
				if isinstance(payload_tick, int):
					event_tick = payload_tick
			if isinstance(event_tick, int):
				if last_tick is not None and event_tick < last_tick:
					with log_file.open("w", encoding="utf-8"):
						pass
				last_tick = event_tick


			#only keep necessary fields jargon
			with log_file.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event))
				handle.write("\n")
	finally:
		channel.close()
