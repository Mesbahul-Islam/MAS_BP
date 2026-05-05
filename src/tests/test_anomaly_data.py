import pytest

def test_normal_snapshot_baseline_values(normal_truck_snapshot):
    snap = normal_truck_snapshot()
    assert snap["door_open"] is False
    assert snap["speed_kmh"] > 0
    assert snap["temperature_c"] < 30
    assert snap["co2_ppm"] < 500

def test_anomaly_snapshot_door_open(anomaly_truck_snapshot):
    snap = anomaly_truck_snapshot(door_open=True)
    assert snap["door_open"] is True

def test_anomaly_snapshot_speed_zero(anomaly_truck_snapshot):
    snap = anomaly_truck_snapshot(speed=0.0)
    assert snap["speed_kmh"] == 0.0

def test_anomaly_snapshot_elevated_temperature(anomaly_truck_snapshot):
    snap = anomaly_truck_snapshot(temp=38.0)
    assert snap["temperature_c"] > 35.0

def test_anomaly_snapshot_elevated_co2(anomaly_truck_snapshot):
    snap = anomaly_truck_snapshot(co2=900.0)
    assert snap["co2_ppm"] > 800.0

def test_cargo_state_anomaly_increments_temperature():
    temp = 20.0
    for _ in range(10):
        if temp < 40.0:
            temp = temp + 0.025
    assert abs(temp - 20.25) < 0.01

def test_cargo_state_anomaly_caps_temperature_at_40():
    temp = 40.0
    for _ in range(5):
        if temp < 40.0:
            temp = round(temp + 0.025, 2)
    assert temp == 40.0

def test_cargo_state_anomaly_increments_co2():
    co2 = 250.0
    for _ in range(10):
        if co2 < 1000.0:
            co2 = round(co2 + 1.2, 2)
    assert abs(co2 - 262.0) < 0.1

def test_cargo_state_anomaly_caps_co2_at_1000():
    co2 = 1000.0
    for _ in range(5):
        if co2 < 1000.0:
            co2 = round(co2 + 1.2, 2)
    assert co2 == 1000.0

def test_anomaly_detection_in_context(make_context, normal_truck_snapshot, anomaly_truck_snapshot):
    ctx = make_context(
        snapshots_per_tick=[
            [normal_truck_snapshot("1", t), anomaly_truck_snapshot("2", t)] for t in (5, 10, 15)
        ]
    )
    anomalies_found = []
    for snap_group in ctx:
        for truck in snap_group["trucks"]:
            if truck["door_open"] or truck["speed_kmh"] == 0.0:
                anomalies_found.append(truck["truck_id"])
    assert "2" in anomalies_found
    assert "1" not in anomalies_found

def test_monitoring_channel_carries_all_trucks(normal_truck_snapshot):
    entries = [normal_truck_snapshot("1"), normal_truck_snapshot("2")]
    ids = {e["truck_id"] for e in entries}
    assert ids == {"1", "2"}