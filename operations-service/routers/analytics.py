from fastapi import APIRouter, Query
from typing import Optional
from db import _http_post

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/revenue/total")
def get_total_revenue(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get total revenue, optionally filtered by date range"""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"timestamp >= '{start_date} 00:00:00'")
    if end_date:
        where_clauses.append(f"timestamp <= '{end_date} 23:59:59'")
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    query = f"""
        SELECT 
            sum(amount) as total_revenue,
            count(*) as total_payments,
            avg(amount) as average_payment
        FROM payments 
        {where_clause}
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [{}])[0] if data.get("data") else {}


@router.get("/revenue/by-class")
def get_revenue_by_class(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get revenue grouped by class"""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"timestamp >= '{start_date} 00:00:00'")
    if end_date:
        where_clauses.append(f"timestamp <= '{end_date} 23:59:59'")
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    query = f"""
        SELECT 
            class_id,
            sum(amount) as total_revenue,
            count(*) as payment_count,
            avg(amount) as average_payment
        FROM payments 
        {where_clause}
        GROUP BY class_id
        ORDER BY total_revenue DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/classes/attendance-stats")
def get_class_attendance_stats(class_id: Optional[str] = Query(None)):
    """Get attendance statistics for classes"""
    where_clause = f"WHERE class_id = '{class_id}'" if class_id else ""
    
    query = f"""
        SELECT 
            class_id,
            count(*) as total_attendances,
            countIf(status = 'checked-in') as checked_in_count,
            countIf(status = 'checked-out') as checked_out_count,
            countIf(status = 'cancelled') as cancelled_count
        FROM attendances
        {where_clause}
        GROUP BY class_id
        ORDER BY total_attendances DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    result = data.get("data", [])
    return result[0] if class_id and result else result


@router.get("/trainers/utilization")
def get_trainer_utilization():
    """Get trainer utilization statistics"""
    query = """
        SELECT 
            trainer_id,
            count(*) as total_classes,
            min(start_time) as first_class,
            max(end_time) as last_class
        FROM classes
        WHERE trainer_id IS NOT NULL
        GROUP BY trainer_id
        ORDER BY total_classes DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/rooms/occupancy")
def get_room_occupancy():
    """Get room occupancy statistics"""
    query = """
        SELECT 
            room_id,
            count(*) as total_classes,
            min(start_time) as first_class,
            max(end_time) as last_class
        FROM classes
        WHERE room_id IS NOT NULL
        GROUP BY room_id
        ORDER BY total_classes DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/members/activity")
def get_member_activity(member_id: Optional[str] = Query(None)):
    """Get member activity statistics"""
    where_clause = f"WHERE member_id = '{member_id}'" if member_id else ""
    
    query = f"""
        SELECT 
            member_id,
            count(*) as total_attendances,
            min(timestamp) as first_attendance,
            max(timestamp) as last_attendance
        FROM attendances
        {where_clause}
        GROUP BY member_id
        ORDER BY total_attendances DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    result = data.get("data", [])
    return result[0] if member_id and result else result


@router.get("/classes/capacity-utilization")
def get_class_capacity_utilization():
    """Get class capacity utilization (attendances vs capacity)"""
    query = """
        SELECT 
            c.class_id,
            c.name,
            c.capacity,
            count(a.event_id) as actual_attendances,
            CASE 
                WHEN c.capacity > 0 THEN round((count(a.event_id) * 100.0) / c.capacity, 2)
                ELSE 0
            END as utilization_percentage
        FROM classes c
        LEFT JOIN attendances a ON c.class_id = a.class_id
        WHERE c.capacity IS NOT NULL
        GROUP BY c.class_id, c.name, c.capacity
        ORDER BY utilization_percentage DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])


@router.get("/revenue/daily")
def get_daily_revenue(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get daily revenue breakdown"""
    where_clauses = []
    
    if start_date:
        where_clauses.append(f"timestamp >= '{start_date} 00:00:00'")
    if end_date:
        where_clauses.append(f"timestamp <= '{end_date} 23:59:59'")
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    query = f"""
        SELECT 
            toDate(timestamp) as date,
            sum(amount) as daily_revenue,
            count(*) as payment_count,
            avg(amount) as average_payment
        FROM payments
        {where_clause}
        GROUP BY date
        ORDER BY date DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    return data.get("data", [])
