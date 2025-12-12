"""
Business logic validation utilities for the operations service
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def _to_aware_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware in UTC"""
    if dt.tzinfo is None or dt.utcoffset() is None:
        # Treat naive as UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fmt_clickhouse(dt: datetime) -> str:
    """Format datetime for ClickHouse (naive string) using UTC"""
    utc = _to_aware_utc(dt)
    return utc.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')


def validate_class_times(start_time: datetime, end_time: datetime) -> None:
    """Validate class start and end times (timezone-safe)"""
    s = _to_aware_utc(start_time)
    e = _to_aware_utc(end_time)
    if s >= e:
        raise ValidationError("Class start time must be before end time", "start_time")
    
    # Prevent booking classes in the past (compare in UTC)
    if s < datetime.now(timezone.utc):
        raise ValidationError("Cannot create classes in the past", "start_time")


def validate_class_capacity(capacity: Optional[int]) -> None:
    """Validate class capacity"""
    if capacity is not None and capacity <= 0:
        raise ValidationError("Class capacity must be positive", "capacity")


def validate_payment_amount(amount: float) -> None:
    """Validate payment amount"""
    if amount <= 0:
        raise ValidationError("Payment amount must be positive", "amount")


def validate_trainer_rating(rating: Optional[float]) -> None:
    """Validate trainer rating"""
    if rating is not None and (rating < 0 or rating > 5):
        raise ValidationError("Trainer rating must be between 0 and 5", "rating")


def validate_attendance_status(status: str) -> None:
    """Validate attendance status"""
    valid_statuses = ["confirmed", "checked-in", "checked-out", "cancelled"]
    if status not in valid_statuses:
        raise ValidationError(
            f"Invalid attendance status. Must be one of: {', '.join(valid_statuses)}", 
            "status"
        )


def check_room_availability(db, room_id: UUID, start_time: datetime, end_time: datetime, 
                            exclude_class_id: Optional[UUID] = None) -> None:
    """Check if room is available for the given time slot"""
    from db import _http_post
    
    exclude_clause = f"AND class_id != '{exclude_class_id}'" if exclude_class_id else ""
    
    start_str = _fmt_clickhouse(start_time)
    end_str = _fmt_clickhouse(end_time)

    query = f"""
        SELECT class_id, name, start_time, end_time
        FROM classes
        WHERE room_id = '{room_id}'
        AND (
            (start_time <= '{start_str}' 
             AND end_time > '{start_str}')
            OR
            (start_time < '{end_str}' 
             AND end_time >= '{end_str}')
            OR
            (start_time >= '{start_str}' 
             AND end_time <= '{end_str}')
        )
        {exclude_clause}
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    conflicts = data.get("data", [])
    
    if conflicts:
        conflict = conflicts[0]
        raise ValidationError(
            f"Room is not available. Conflicts with class '{conflict['name']}' "
            f"from {conflict['start_time']} to {conflict['end_time']}",
            "room_id"
        )


def check_trainer_availability(db, trainer_id: UUID, start_time: datetime, end_time: datetime,
                                exclude_class_id: Optional[UUID] = None) -> None:
    """Check if trainer is available for the given time slot"""
    from db import _http_post
    
    exclude_clause = f"AND class_id != '{exclude_class_id}'" if exclude_class_id else ""
    
    start_str = _fmt_clickhouse(start_time)
    end_str = _fmt_clickhouse(end_time)

    query = f"""
        SELECT class_id, name, start_time, end_time
        FROM classes
        WHERE trainer_id = '{trainer_id}'
        AND (
            (start_time <= '{start_str}' 
             AND end_time > '{start_str}')
            OR
            (start_time < '{end_str}' 
             AND end_time >= '{end_str}')
            OR
            (start_time >= '{start_str}' 
             AND end_time <= '{end_str}')
        )
        {exclude_clause}
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    conflicts = data.get("data", [])
    
    if conflicts:
        conflict = conflicts[0]
        raise ValidationError(
            f"Trainer is not available. Conflicts with class '{conflict['name']}' "
            f"from {conflict['start_time']} to {conflict['end_time']}",
            "trainer_id"
        )


def check_class_capacity(db, class_id: UUID) -> Dict[str, Any]:
    """Check class capacity and return capacity info"""
    from db import _http_post
    
    # Get class capacity
    class_query = f"""
        SELECT capacity, name
        FROM classes
        WHERE class_id = '{class_id}'
        FORMAT JSON
    """
    
    resp = _http_post(class_query)
    data = resp.json()
    class_data = data.get("data", [])
    
    if not class_data:
        raise ValidationError("Class not found", "class_id")
    
    class_info = class_data[0]
    capacity = class_info.get("capacity")
    
    if capacity is None:
        # No capacity limit
        return {
            "capacity": None,
            "current_count": 0,
            "available": True,
            "class_name": class_info.get("name")
        }
    
    # Count current attendances
    attendance_query = f"""
        SELECT count(*) as count
        FROM attendances
        WHERE class_id = '{class_id}'
        AND status != 'cancelled'
        FORMAT JSON
    """
    
    resp = _http_post(attendance_query)
    data = resp.json()
    count_data = data.get("data", [{}])[0]
    current_count = count_data.get("count", 0)
    
    return {
        "capacity": capacity,
        "current_count": current_count,
        "available": current_count < capacity,
        "available_spots": capacity - current_count,
        "class_name": class_info.get("name")
    }


def validate_class_not_full(db, class_id: UUID) -> None:
    """Validate that class has available capacity"""
    capacity_info = check_class_capacity(db, class_id)
    
    if not capacity_info["available"]:
        raise ValidationError(
            f"Class '{capacity_info['class_name']}' is full "
            f"({capacity_info['current_count']}/{capacity_info['capacity']} attendees)",
            "class_id"
        )


def validate_foreign_keys(db, class_id: Optional[UUID] = None, 
                         trainer_id: Optional[UUID] = None,
                         room_id: Optional[UUID] = None,
                         member_id: Optional[UUID] = None) -> None:
    """Validate that foreign key references exist"""
    from db import select_one
    
    if class_id:
        result = select_one("classes", "class_id", str(class_id))
        if not result:
            raise ValidationError(f"Class with ID {class_id} not found", "class_id")
    
    if trainer_id:
        result = select_one("trainers", "trainer_id", str(trainer_id))
        if not result:
            raise ValidationError(f"Trainer with ID {trainer_id} not found", "trainer_id")
    
    if room_id:
        result = select_one("rooms", "room_id", str(room_id))
        if not result:
            raise ValidationError(f"Room with ID {room_id} not found", "room_id")
    
    # Note: member_id validation would require integration with member service
    # For now, we skip it as it's managed by another team


def validate_payment_before_attendance(db, class_id: UUID, member_id: UUID) -> None:
    """Validate that member has paid before checking in"""
    from db import _http_post
    
    query = f"""
        SELECT payment_id
        FROM payments
        WHERE class_id = '{class_id}'
        AND member_id = '{member_id}'
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    payments = data.get("data", [])
    
    if not payments:
        raise ValidationError(
            "Payment required before attendance can be recorded",
            "member_id"
        )


def validate_not_past_class(db, class_id: UUID, operation: str = "cancel") -> None:
    """Validate that class hasn't ended yet"""
    from db import select_one
    
    class_data = select_one("classes", "class_id", str(class_id))
    if not class_data:
        raise ValidationError("Class not found", "class_id")
    
    end_time = datetime.fromisoformat(class_data["end_time"]) if isinstance(class_data["end_time"], str) else class_data["end_time"]
    
    if end_time < datetime.now():
        raise ValidationError(
            f"Cannot {operation} attendance for a class that has already ended",
            "class_id"
        )
