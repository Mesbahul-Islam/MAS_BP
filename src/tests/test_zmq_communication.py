import pytest
import threading
from simulation.communication import ZeroMQTelemetryChannel

def _make_channel_pair(fake_socket_class, topic="test"):
    pub = ZeroMQTelemetryChannel(endpoint="tcp://127.0.0.1:5599", topic=topic)
    sub = ZeroMQTelemetryChannel(endpoint="tcp://127.0.0.1:5599", topic=topic)
    shared_socket = fake_socket_class(None)
    pub._ensure_publisher()
    pub._publisher = shared_socket
    sub._subscriber = shared_socket
    return pub, sub

def test_publish_returns_event_envelope(fake_socket_class):
    pub, _ = _make_channel_pair(fake_socket_class)
    event = pub.publish(tick=1, source_agent="truck_1", payload={"truck_id": "1", "speed_kmh": 80.0})
    assert "tick" in event
    assert "payload" in event
    assert event["tick"] == 1
    assert event["source_agent"] == "truck_1"

def test_subscribe_receives_published_event(fake_socket_class):
    pub, sub = _make_channel_pair(fake_socket_class)
    payload = {"truck_id": "1", "speed_kmh": 75.0}
    pub.publish(tick=5, source_agent="truck_1", payload=payload)
    received = sub.subscribe(block=False)
    assert received is not None
    assert received["payload"]["speed_kmh"] == 75.0

def test_message_id_increments_per_truck(fake_socket_class):
    pub, _ = _make_channel_pair(fake_socket_class)
    e1 = pub.publish(tick=1, source_agent="truck_1", payload={"truck_id": "1"})
    e2 = pub.publish(tick=2, source_agent="truck_1", payload={"truck_id": "1"})
    assert e1["message_id"] == 0
    assert e2["message_id"] == 1

def test_message_id_separate_per_truck(fake_socket_class):
    pub, _ = _make_channel_pair(fake_socket_class)
    e_t1 = pub.publish(tick=1, source_agent="t1", payload={"truck_id": "1"})
    e_t2 = pub.publish(tick=1, source_agent="t2", payload={"truck_id": "2"})
    assert e_t1["message_id"] == 0
    assert e_t2["message_id"] == 0

def test_subscribe_nonblocking_returns_none_when_empty(fake_socket_class):
    sub = ZeroMQTelemetryChannel(endpoint="tcp://127.0.0.1:5598", topic="empty")
    sub._subscriber = fake_socket_class(None)  # empty queue
    result = sub.subscribe(block=False)
    assert result is None

def test_multiple_events_queued_and_received_in_order(fake_socket_class):
    pub, sub = _make_channel_pair(fake_socket_class, topic="order_test")
    for i in range(5):
        pub.publish(tick=i, source_agent="truck_1", payload={"truck_id": "1", "seq": i})
    received_seqs = []
    for _ in range(5):
        ev = sub.subscribe(block=False)
        if ev:
            received_seqs.append(ev["payload"]["seq"])
    assert received_seqs == list(range(5))

def test_close_marks_subscriber_none(fake_socket_class):
    ch = ZeroMQTelemetryChannel(endpoint="tcp://127.0.0.1:5597", topic="close_test")
    ch._subscriber = fake_socket_class(None)
    ch.close()
    assert ch._subscriber is None

def test_event_contains_utc_timestamp(fake_socket_class):
    pub, _ = _make_channel_pair(fake_socket_class)
    event = pub.publish(tick=1, source_agent="t1", payload={"truck_id": "1"})
    assert "timestamp_utc" in event
    assert event["timestamp_utc"].endswith("+00:00") or "Z" in event["timestamp_utc"] or "T" in event["timestamp_utc"]

def test_payload_is_json_serializable(fake_socket_class):
    pub, sub = _make_channel_pair(fake_socket_class)
    payload = {"truck_id": "99", "speed_kmh": 55.5, "door_open": True}
    pub.publish(tick=3, source_agent="truck_99", payload=payload)
    received = sub.subscribe(block=False)
    assert received["payload"]["door_open"] is True

def test_concurrent_publishers_dont_corrupt_messages(fake_socket_class):
    pub, sub = _make_channel_pair(fake_socket_class, topic="concurrent")
    errors = []

    def publish_n(truck_id, n):
        for i in range(n):
            try:
                pub.publish(tick=i, source_agent=f"truck_{truck_id}", payload={"truck_id": truck_id, "idx": i})
            except Exception as e:
                errors.append(e)

    t1 = threading.Thread(target=publish_n, args=("A", 10))
    t2 = threading.Thread(target=publish_n, args=("B", 10))
    t1.start(); t2.start()
    t1.join(); t2.join()
    assert errors == []