"""SQLite database layer for PostCare Companion.

All times are stored as text in the format YYYY-MM-DD HH:MM:SS so they
sort correctly and can be compared as strings.
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]      # repo root folder
DB_PATH = ROOT / "postcare.db"
VITALS_CSV = ROOT / "data" / "simulated_vitals.csv"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    age_group  TEXT,
    sex        TEXT
);

CREATE TABLE IF NOT EXISTS plans (
    plan_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     TEXT NOT NULL,
    diagnosis      TEXT,
    discharge_date TEXT,
    plan_json      TEXT NOT NULL,
    created_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id        INTEGER NOT NULL,
    patient_id     TEXT NOT NULL,
    type           TEXT NOT NULL,
    title          TEXT NOT NULL,
    due_time       TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    completed_time TEXT
);

CREATE TABLE IF NOT EXISTS checkins (
    checkin_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   TEXT NOT NULL,
    date         TEXT NOT NULL,
    answers_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vitals (
    vital_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    timestamp  TEXT NOT NULL,
    temp_c     REAL,
    heart_rate REAL,
    spo2       REAL,
    systolic   REAL,
    diastolic  REAL,
    resp_rate  REAL,
    weight_kg  REAL,
    source     TEXT DEFAULT 'manual'
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    TEXT NOT NULL,
    level         TEXT NOT NULL,
    reason        TEXT NOT NULL,
    created_time  TEXT NOT NULL,
    acknowledged  INTEGER NOT NULL DEFAULT 0
);
"""


def now_str():
    """Current time as text in the database time format."""
    return datetime.now().strftime(TIME_FORMAT)


@contextmanager
def connect():
    """Open the database, save changes on success, always close."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not exist yet."""
    with connect() as conn:
        conn.executescript(SCHEMA)


def _rows(cursor):
    """Turn query results into a list of plain dictionaries."""
    return [dict(r) for r in cursor.fetchall()]

# ---------- Patients and plans ----------

def save_patient(patient_id, age_group=None, sex=None):
    """Add a patient (or update if the ID already exists)."""
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO patients (patient_id, age_group, sex) "
            "VALUES (?, ?, ?)",
            (patient_id, age_group, sex),
        )


def list_patients():
    with connect() as conn:
        return _rows(conn.execute("SELECT * FROM patients ORDER BY patient_id"))


def save_plan(patient_id, plan):
    """Save a confirmed recovery plan (a dict) and return its plan_id."""
    admission = plan.get("admission", {})
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO plans (patient_id, diagnosis, discharge_date, plan_json) "
            "VALUES (?, ?, ?, ?)",
            (
                patient_id,
                admission.get("primary_diagnosis"),
                admission.get("discharge_date"),
                json.dumps(plan),
            ),
        )
        return cur.lastrowid


def _plan_from_row(row):
    if row is None:
        return None
    data = dict(row)
    data["plan"] = json.loads(data.pop("plan_json"))
    return data


def get_plan(plan_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM plans WHERE plan_id = ?", (plan_id,)
        ).fetchone()
    return _plan_from_row(row)


def get_latest_plan(patient_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM plans WHERE patient_id = ? ORDER BY plan_id DESC LIMIT 1",
            (patient_id,),
        ).fetchone()
    return _plan_from_row(row)

# ---------- Events ----------

VALID_STATUSES = ("pending", "done", "missed")


def save_events(plan_id, patient_id, events):
    """Save a list of events. Each event is a dict with type, title, due_time."""
    with connect() as conn:
        conn.executemany(
            "INSERT INTO events (plan_id, patient_id, type, title, due_time) "
            "VALUES (?, ?, ?, ?, ?)",
            [(plan_id, patient_id, e["type"], e["title"], e["due_time"]) for e in events],
        )
    return len(events)


def get_events(patient_id, status=None, start=None, end=None):
    """Events for a patient, optionally filtered by status and a time window."""
    query = "SELECT * FROM events WHERE patient_id = ?"
    params = [patient_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    if start:
        query += " AND due_time >= ?"
        params.append(start)
    if end:
        query += " AND due_time <= ?"
        params.append(end)
    query += " ORDER BY due_time"
    with connect() as conn:
        return _rows(conn.execute(query, params))


def update_event_status(event_id, status, completed_time=None):
    """Set an event to pending, done or missed."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}")
    if status == "done" and completed_time is None:
        completed_time = now_str()
    with connect() as conn:
        conn.execute(
            "UPDATE events SET status = ?, completed_time = ? WHERE event_id = ?",
            (status, completed_time, event_id),
        )

# ---------- Check-ins ----------

def save_checkin(patient_id, date, answers):
    """Save one daily check-in. answers is a dict, for example {"pain": 4}."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO checkins (patient_id, date, answers_json) VALUES (?, ?, ?)",
            (patient_id, date, json.dumps(answers)),
        )


def get_checkins(patient_id):
    with connect() as conn:
        rows = _rows(conn.execute(
            "SELECT * FROM checkins WHERE patient_id = ? ORDER BY date", (patient_id,)
        ))
    for r in rows:
        r["answers"] = json.loads(r.pop("answers_json"))
    return rows


# ---------- Vitals ----------

VITAL_COLUMNS = ["temp_c", "heart_rate", "spo2", "systolic",
                 "diastolic", "resp_rate", "weight_kg"]
_INSERT_VITALS = (
    "INSERT INTO vitals (patient_id, timestamp, temp_c, heart_rate, spo2, "
    "systolic, diastolic, resp_rate, weight_kg, source) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


def save_vitals(patient_id, timestamp, source="manual", **values):
    """Save one vitals reading. Missing vitals are stored as empty (NULL)."""
    row = [patient_id, timestamp] + [values.get(c) for c in VITAL_COLUMNS] + [source]
    with connect() as conn:
        conn.execute(_INSERT_VITALS, row)


def get_vitals(patient_id):
    with connect() as conn:
        return _rows(conn.execute(
            "SELECT * FROM vitals WHERE patient_id = ? ORDER BY timestamp", (patient_id,)
        ))


def load_simulated_vitals(csv_path=None):
    """Import MedElec-2's simulated vitals CSV. Safe to run more than once."""
    path = Path(csv_path) if csv_path else VITALS_CSV
    columns = ["patient_id", "timestamp"] + VITAL_COLUMNS + ["source"]
    df = pd.read_csv(path)
    df["source"] = "simulated"
    df = df.reindex(columns=columns)
    df = df.astype(object).where(pd.notna(df), None)   # empty cells become NULL
    records = [tuple(row[c] for c in columns) for _, row in df.iterrows()]
    with connect() as conn:
        conn.execute("DELETE FROM vitals WHERE source = 'simulated'")
        for pid in df["patient_id"].unique():
            conn.execute("INSERT OR IGNORE INTO patients (patient_id) VALUES (?)", (pid,))
        conn.executemany(_INSERT_VITALS, records)
    return len(records)

# ---------- Alerts ----------

def save_alert(patient_id, level, reason):
    """Create an alert (level is 'red' or 'amber') and return its alert_id."""
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO alerts (patient_id, level, reason, created_time) "
            "VALUES (?, ?, ?, ?)",
            (patient_id, level, reason, now_str()),
        )
        return cur.lastrowid


def get_alerts(patient_id=None, only_open=False):
    """Alerts, newest first. only_open=True hides acknowledged alerts."""
    query = "SELECT * FROM alerts WHERE 1 = 1"
    params = []
    if patient_id:
        query += " AND patient_id = ?"
        params.append(patient_id)
    if only_open:
        query += " AND acknowledged = 0"
    query += " ORDER BY created_time DESC, alert_id DESC"
    with connect() as conn:
        return _rows(conn.execute(query, params))


def acknowledge_alert(alert_id):
    with connect() as conn:
        conn.execute("UPDATE alerts SET acknowledged = 1 WHERE alert_id = ?", (alert_id,))


if __name__ == "__main__":
    init_db()
    print("Database ready at", DB_PATH)