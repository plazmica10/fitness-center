from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from db import select_by_filters, _http_post
import json

router = APIRouter(prefix="/queries", tags=["queries"])


@router.get("/classes/by-trainer/{trainer_id}")
def get_classes_by_trainer(trainer_id: str):
    """Get all classes for a specific trainer"""
    filters = {"trainer_id": trainer_id}
    rows = select_by_filters("classes", filters, order_by="start_time")
    return rows


@router.get("/classes/by-room/{room_id}")
def get_classes_by_room(room_id: str):
    """Get all classes in a specific room"""
    filters = {"room_id": room_id}
    rows = select_by_filters("classes", filters, order_by="start_time")
    return rows


@router.get("/classes/by-date")
def get_classes_by_date(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get classes within a date range"""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"start_time >= '{start_date} 00:00:00'")
    if end_date:
        where_clauses.append(f"start_time <= '{end_date} 23:59:59'")
    
    if where_clauses:
        where_clause = " AND ".join(where_clauses)
        query = f"SELECT * FROM classes WHERE {where_clause} ORDER BY start_time FORMAT JSON"
    else:
        query = "SELECT * FROM classes ORDER BY start_time FORMAT JSON"
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/payments/by-member/{member_id}")
def get_payments_by_member(member_id: str):
    """Get all payments for a specific member"""
    filters = {"member_id": member_id}
    rows = select_by_filters("payments", filters, order_by="timestamp DESC")
    return rows


@router.get("/payments/by-class/{class_id}")
def get_payments_by_class(class_id: str):
    """Get all payments for a specific class"""
    filters = {"class_id": class_id}
    rows = select_by_filters("payments", filters, order_by="timestamp DESC")
    return rows


@router.get("/payments/by-date-range")
def get_payments_by_date_range(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get payments within a date range"""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"timestamp >= '{start_date} 00:00:00'")
    if end_date:
        where_clauses.append(f"timestamp <= '{end_date} 23:59:59'")
    
    if where_clauses:
        where_clause = " AND ".join(where_clauses)
        query = f"SELECT * FROM payments WHERE {where_clause} ORDER BY timestamp DESC FORMAT JSON"
    else:
        query = "SELECT * FROM payments ORDER BY timestamp DESC FORMAT JSON"
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/attendances/by-class/{class_id}")
def get_attendances_by_class(class_id: str):
    """Get all attendances for a specific class"""
    filters = {"class_id": class_id}
    rows = select_by_filters("attendances", filters, order_by="timestamp DESC")
    return rows


@router.get("/attendances/by-member/{member_id}")
def get_attendances_by_member(member_id: str):
    """Get all attendances for a specific member"""
    filters = {"member_id": member_id}
    rows = select_by_filters("attendances", filters, order_by="timestamp DESC")
    return rows


@router.get("/attendances/by-status/{status}")
def get_attendances_by_status(status: str):
    """Get all attendances with a specific status"""
    filters = {"status": status}
    rows = select_by_filters("attendances", filters, order_by="timestamp DESC")
    return rows


@router.get("/rooms/available")
def get_available_rooms(has_equipment: Optional[bool] = Query(None)):
    """Get rooms, optionally filtered by equipment availability"""
    if has_equipment is not None:
        filters = {"has_equipment": has_equipment}
        rows = select_by_filters("rooms", filters, order_by="capacity DESC")
    else:
        query = "SELECT * FROM rooms ORDER BY capacity DESC FORMAT JSON"
        resp = _http_post(query)
        data = resp.json()
        rows = data.get("data", [])
    return rows


@router.get("/trainers/by-specialization/{specialization}")
def get_trainers_by_specialization(specialization: str):
    """Get trainers by specialization"""
    filters = {"specialization": specialization}
    rows = select_by_filters("trainers", filters, order_by="rating DESC")
    return rows
