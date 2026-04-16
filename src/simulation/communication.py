from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from config import TELEMETRY_ENDPOINT, TELEMETRY_TOPIC
import zmq


@dataclass(frozen=True)
class TelemetryEvent:
	"""Telemetry event schema sent over the pub/sub channel."""
	message_id:str
	timestamp_utc: str
	tick: int
	source_agent: str
	payload: dict[str, Any]

	def to_dict(self) -> dict[str, Any]:
		return {
			"message_id": self.message_id,
			"timestamp_utc": self.timestamp_utc,
			"tick": self.tick,
			"source_agent": self.source_agent,
			"payload": self.payload,
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> TelemetryEvent:
		return cls(
			message_id=str(data["message_id"]),
			timestamp_utc=str(data["timestamp_utc"]),
			tick=int(data["tick"]),
			source_agent=str(data["source_agent"]),
			payload=dict(data["payload"]),
		)


class ZeroMQTelemetryChannel:
	"""Ephemeral ZeroMQ pub/sub channel for truck telemetry events."""

	def __init__(self) -> None:
		self.topic = TELEMETRY_TOPIC
		self.endpoint = TELEMETRY_ENDPOINT
		self.context = zmq.Context()
		self._publisher = self.context.socket(zmq.PUB)
		self._publisher.setsockopt(zmq.LINGER, 0)
		self.message_id_counter = 0
		self._publisher.bind(self.endpoint)

	def publish(self, *, tick: int, source_agent: str, payload: dict[str, Any]) -> TelemetryEvent:
		"""Publish a telemetry event to subscribers.

		Events are not stored in memory by this channel.
		"""
		event = TelemetryEvent(
			message_id=self.message_id_counter,
			timestamp_utc=datetime.now(timezone.utc).isoformat(),
			tick=tick,
			source_agent=source_agent,
			payload=payload,
		)
		self.message_id_counter += 1

		self._publisher.send_multipart(
			[self.topic.encode("utf-8"), json.dumps(event.to_dict()).encode("utf-8")]
		)
		return event

	def close(self) -> None:
		self._publisher.close(linger=0)
		self.context.term()


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
			event = TelemetryEvent.from_dict(payload)

			truck_id = str(event.payload.get("truck_id", "unknown"))
			log_file = output_base / f"truck_{truck_id}" / "output.jsonl"
			log_file.parent.mkdir(parents=True, exist_ok=True)
			with log_file.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event.to_dict()))
				handle.write("\n")
	finally:
		subscriber.close(linger=0)
		context.term()
