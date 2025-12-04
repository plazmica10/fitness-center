from fastapi import APIRouter, HTTPException
from typing import List
from models.payment import Payment
from db import select_all, insert_one, select_one, update_one, delete_one

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=List[Payment])
def list_payments():
    rows = select_all("payments")
    return rows

# TODO: should call member service to verify member_id exists
@router.post("/", response_model=Payment)
def create_payment(payment: Payment):
    payment_dict = payment.dict()
    generated_id = insert_one("payments", payment_dict)
    if generated_id and not payment.payment_id:
        payment.payment_id = generated_id
    return payment


@router.get("/{payment_id}", response_model=Payment)
def get_payment(payment_id: str):
    p = select_one("payments", "payment_id", payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p


@router.put("/{payment_id}", response_model=Payment)
def update_payment(payment_id: str, payment: Payment):
    existing = select_one("payments", "payment_id", payment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_dict = payment.dict()
    update_one("payments", "payment_id", payment_id, payment_dict)
    payment.payment_id = payment_id
    return payment


@router.delete("/{payment_id}")
def delete_payment(payment_id: str):
    existing = select_one("payments", "payment_id", payment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        delete_one("payments", "payment_id", payment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete mutation failed: {e}")
    return {"ok": True}
