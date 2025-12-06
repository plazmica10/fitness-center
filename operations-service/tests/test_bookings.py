from datetime import datetime, timedelta, timezone
from uuid import uuid4
import time
import sys
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Direct tests to local ClickHouse when running outside Docker network
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

import db
import routers.bookings as bookings
from main import app


pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.fixture(autouse=True)
def reset_saga():
    # Clear saga state between tests
    bookings.saga_orchestrator.active.clear()
    yield
    bookings.saga_orchestrator.active.clear()


@pytest.fixture(scope="module")
def client():
    # Ensure tables exist before hitting the API
    db.init_tables()
    with TestClient(app) as c:
        yield c


def _create_class(capacity: int = 3) -> str:
    class_id = str(uuid4())
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=1)
    db.insert_one(
        "classes",
        {
            "class_id": class_id,
            "name": "Integration Yoga",
            "trainer_id": None,
            "room_id": None,
            "start_time": start,
            "end_time": end,
            "capacity": capacity,
            "price": 10.0,
            "description": "",
        },
    )
    return class_id


def _cleanup_rows(attendance_id: str | None, payment_id: str | None, class_id: str) -> None:
    # Compensation and tests issue async deletes in ClickHouse; best effort cleanup
    if attendance_id:
        try:
            db.delete_one("attendances", "event_id", attendance_id)
        except Exception:
            pass
    if payment_id:
        try:
            db.delete_one("payments", "payment_id", payment_id)
        except Exception:
            pass
    try:
        db.delete_one("classes", "class_id", class_id)
    except Exception:
        pass


def _wait_for_absence(table: str, key: str, value: str, retries: int = 5, delay: float = 0.2) -> bool:
    for _ in range(retries):
        if db.select_one(table, key, value) is None:
            return True
        time.sleep(delay)
    return db.select_one(table, key, value) is None

def test_successful_booking_clickhouse(client, capsys):
    class_id = _create_class()
    attendance_id = payment_id = None
    member_id = str(uuid4())
    try:
        payload = {"member_id": member_id, "class_id": class_id, "amount": 15.5}
        resp = client.post("/bookings/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success", data

        attendance_id = data["attendance_id"]
        payment_id = data["payment_id"]

        attendance = db.select_one("attendances", "event_id", attendance_id)
        payment = db.select_one("payments", "payment_id", payment_id)

        assert attendance is not None
        assert payment is not None
        assert attendance.get("class_id") == class_id
        assert payment.get("member_id") == member_id
    finally:
        _cleanup_rows(attendance_id, payment_id, class_id)


def test_failed_booking_compensates_clickhouse(monkeypatch, client, capsys):
    class_id = _create_class(capacity=1)
    attendance_id = None
    member_id = str(uuid4())

    real_insert_one = bookings.insert_one

    def failing_payment_insert(table, record):
        if table == "payments":
            raise RuntimeError("payment insert failed")
        return real_insert_one(table, record)

    monkeypatch.setattr(bookings, "insert_one", failing_payment_insert)

    try:
        payload = {"member_id": member_id, "class_id": class_id, "amount": 20.0}
        resp = client.post("/bookings/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "failed"

        # Attendance should have been compensated after payment failure
        attendances = db.select_by_filters("attendances", {"class_id": class_id, "member_id": member_id})
        if attendances:
            attendance_id = attendances[0].get("event_id")
            assert _wait_for_absence("attendances", "event_id", attendance_id)
        assert db.select_by_filters("payments", {"class_id": class_id, "member_id": member_id}) == []
    finally:
        _cleanup_rows(attendance_id, None, class_id)
