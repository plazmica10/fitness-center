from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Any, Dict

from saga.orchestrator import saga_orchestrator
from services.member_service_client import member_service_client
from db import insert_one, delete_one, select_one
from utils.validators import validate_foreign_keys, validate_class_not_full, ValidationError

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingRequest(BaseModel):
    member_id: str
    class_id: str
    amount: float


class BookingResponse(BaseModel):
    transaction_id: str
    status: str
    attendance_id: str | None = None
    payment_id: str | None = None
    error: str | None = None


@router.post("/", response_model=BookingResponse)
async def create_booking(payload: BookingRequest):
    """
    Booking transaction across two microservices (future member service + current operations service).
    Member-service steps are placeholders until that service is implemented.
    """
    results: Dict[str, Any] = {}
    tx_id = saga_orchestrator.create_transaction()

    # Step 1: placeholder reservation in member service (no-op for now)
    async def reserve_member():
        res = await member_service_client.reserve_slot(payload.member_id, payload.class_id)
        results["member_reservation"] = res
        return res

    async def compensate_reserve():
        if "member_reservation" in results:
            return await member_service_client.cancel_reservation(
                payload.member_id, results["member_reservation"].get("reservation_id", "")
            )
        return {}

    saga_orchestrator.add_step(tx_id, "reserve_member", reserve_member, compensate_reserve)

    # Step 2: validate class in ClickHouse
    async def validate_class():
        try:
            validate_foreign_keys(None, class_id=payload.class_id)
            validate_class_not_full(None, payload.class_id)
            cls = select_one("classes", "class_id", payload.class_id)
            if not cls:
                raise ValidationError("Class not found", "class_id")
            results["class"] = cls
            return cls
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)

    async def compensate_validate_class():
        return {}

    saga_orchestrator.add_step(tx_id, "validate_class", validate_class, compensate_validate_class)

    # Step 3: create attendance in ClickHouse
    async def create_attendance():
        attendance = {
            "class_id": payload.class_id,
            "member_id": payload.member_id,
            "timestamp": datetime.now(timezone.utc),
            "status": "checked-in",
        }
        att_id = insert_one("attendances", attendance)
        results["attendance_id"] = att_id
        return {"attendance_id": att_id}

    async def compensate_attendance():
        if "attendance_id" in results:
            delete_one("attendances", "event_id", results["attendance_id"])
        return {}

    saga_orchestrator.add_step(tx_id, "create_attendance", create_attendance, compensate_attendance)

    # Step 4: placeholder record payment in member service (no-op for now)
    async def record_member_payment():
        res = await member_service_client.record_payment(payload.member_id, payload.amount, payload.class_id)
        results["member_payment"] = res
        return res

    async def compensate_member_payment():
        if "member_payment" in results:
            return await member_service_client.refund_payment(
                payload.member_id, results["member_payment"].get("payment_id", "")
            )
        return {}

    saga_orchestrator.add_step(tx_id, "record_member_payment", record_member_payment, compensate_member_payment)

    # Step 5: create payment in ClickHouse
    async def create_payment():
        payment = {
            "class_id": payload.class_id,
            "member_id": payload.member_id,
            "amount": payload.amount,
            "timestamp": datetime.now(timezone.utc),
            "status": "completed",
        }
        pay_id = insert_one("payments", payment)
        results["payment_id"] = pay_id
        return {"payment_id": pay_id}

    async def compensate_payment():
        if "payment_id" in results:
            delete_one("payments", "payment_id", results["payment_id"])
        return {}

    saga_orchestrator.add_step(tx_id, "create_payment", create_payment, compensate_payment)

    # Execute saga
    exec_result = await saga_orchestrator.execute(tx_id)
    status = exec_result.get("status")
    if status == "completed":
        return BookingResponse(
            transaction_id=tx_id,
            status="success",
            attendance_id=results.get("attendance_id"),
            payment_id=results.get("payment_id"),
        )
    return BookingResponse(transaction_id=tx_id, status="failed", error=exec_result.get("error"))


@router.get("/{transaction_id}/status")
async def get_booking_status(transaction_id: str):
    try:
        return saga_orchestrator.get_status(transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
