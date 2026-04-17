from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

from config import TELEMETRY_ENDPOINT, TELEMETRY_TOPIC
from simulation.schemas import (
	AgentEvent,
	TRUCK_TELEMETRY_SCHEMA,
	TruckTelemetryPayload,
)
import zmq


_publisher_lock = threading.Lock()
_shared_publishers: dict[str, dict] = {}


class ZeroMQTelemetryChannel:
	"""Ephemeral ZeroMQ pub/sub channel for truck telemetry events."""

	def __init__(self) -> None:
		self.topic = TELEMETRY_TOPIC
		self.endpoint = TELEMETRY_ENDPOINT
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

	def publish(self, *, tick: int, source_agent: str, payload: TruckTelemetryPayload) -> AgentEvent:
		"""Publish a telemetry event to subscribers.

		Events are not stored in memory by this channel.
		"""
		# message id not shared anymore
		truck_key = str(payload.get("truck_id", source_agent))
		message_id = self.message_id_counters.get(truck_key, 0)
		self.message_id_counters[truck_key] = message_id + 1

		event: AgentEvent = {
			"schema": TRUCK_TELEMETRY_SCHEMA,
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

	def close(self) -> None:
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


def run_telemetry_subscriber(endpoint: str, topic: str, output_root: str) -> None:
	"""Subscribe to telemetry events and append JSON lines into per-truck JSONL files."""
	output_base = Path(output_root)
	output_base.mkdir(parents=True, exist_ok=True)

	context = zmq.Context()
	subscriber = context.socket(zmq.SUB)
	subscriber.connect(endpoint)
	subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

	try:
		while True:
			_ignored_topic, raw_payload = subscriber.recv_multipart()
			payload = json.loads(raw_payload.decode("utf-8"))
			event = cast(AgentEvent, payload)
			if event["schema"] != TRUCK_TELEMETRY_SCHEMA:
				continue
			truck_payload = cast(TruckTelemetryPayload, event["payload"])

			truck_id = str(truck_payload["truck_id"])
			log_file = output_base / f"truck_{truck_id}" / "output.jsonl"
			log_file.parent.mkdir(parents=True, exist_ok=True)
			with log_file.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event))
				handle.write("\n")
	finally:
		subscriber.close(linger=0)
		context.term()
