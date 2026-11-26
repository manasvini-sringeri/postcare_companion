import pytest

import db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test gets its own empty database, so tests never touch real data."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()


SAMPLE_PLAN = {
    "admission": {
        "primary_diagnosis": "Right total knee replacement",
        "discharge_date": "2026-11-15",
    },
    "medications": [{"name": "Paracetamol", "dose": "500 mg", "frequency_per_day": 3}],
}


def test_save_and_load_plan():
    db.save_patient("P100", "60-70", "F")
    plan_id = db.save_plan("P100", SAMPLE_PLAN)
    loaded = db.get_latest_plan("P100")
    assert loaded["plan_id"] == plan_id
    assert loaded["diagnosis"] == "Right total knee replacement"
    assert loaded["plan"]["medications"][0]["name"] == "Paracetamol"


def test_events_flow():
    db.save_patient("P100")
    plan_id = db.save_plan("P100", SAMPLE_PLAN)
    db.save_events(plan_id, "P100", [
        {"type": "medicine", "title": "Paracetamol 500 mg", "due_time": "2026-11-16 08:00:00"},
        {"type": "medicine", "title": "Paracetamol 500 mg", "due_time": "2026-11-16 14:00:00"},
    ])
    events = db.get_events("P100")
    assert len(events) == 2
    assert events[0]["status"] == "pending"
    db.update_event_status(events[0]["event_id"], "done")
    assert len(db.get_events("P100", status="done")) == 1
    assert len(db.get_events("P100", start="2026-11-16 12:00:00")) == 1


def test_invalid_status():
    with pytest.raises(ValueError):
        db.update_event_status(1, "finished")


def test_checkin_and_vitals():
    db.save_checkin("P100", "2026-11-16", {"pain": 4, "fever": "no"})
    assert db.get_checkins("P100")[0]["answers"]["pain"] == 4
    db.save_vitals("P100", "2026-11-16 08:00:00", temp_c=37.1, heart_rate=80)
    vitals = db.get_vitals("P100")
    assert vitals[0]["temp_c"] == 37.1
    assert vitals[0]["spo2"] is None


def test_load_simulated_vitals(tmp_path):
    csv = tmp_path / "vitals.csv"
    csv.write_text(
        "patient_id,timestamp,temp_c,heart_rate,spo2,systolic,diastolic,resp_rate,weight_kg,source\n"
        "P001,2026-11-16 08:00,36.8,78,97,120,78,16,,simulated\n"
    )
    assert db.load_simulated_vitals(csv) == 1
    assert db.load_simulated_vitals(csv) == 1      # running twice must not duplicate
    assert len(db.get_vitals("P001")) == 1


def test_alerts():
    alert_id = db.save_alert("P100", "red", "SpO2 below 92%")
    assert len(db.get_alerts(only_open=True)) == 1
    db.acknowledge_alert(alert_id)
    assert len(db.get_alerts(only_open=True)) == 0