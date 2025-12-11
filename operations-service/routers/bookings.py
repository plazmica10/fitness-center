"""
Transaction Flow:
1. Validate class exists and has capacity
2. Deduct balance from user (MongoDB)
3. Create payment record (ClickHouse)
4. Create attendance record (ClickHouse)
5. If any step fails, rollback all changes
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

from db import select_one, insert_one, delete_one, update_one, _http_post
from auth_middleware import get_current_user
from services.user_balance_service import (
    deduct_user_balance,
    refund_user_balance,
    InsufficientBalanceError,
    BalanceServiceError
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingRequest(BaseModel):
    class_id: UUID
    member_id: str  # MongoDB user ID


class BookingResponse(BaseModel):
    success: bool
    booking_id: str
    payment_id: str
    attendance_id: str
    class_id: str
    member_id: str
    amount: float
    message: str


class BookingError(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[str] = None


def get_bearer_token(request: Request) -> str:
    """Extract bearer token from request headers"""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header or " " not in auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    return auth_header.split(" ", 1)[1]


@router.post("/book-class", response_model=BookingResponse, responses={
    402: {"model": BookingError, "description": "Insufficient balance"},
    404: {"model": BookingError, "description": "Class or user not found"},
    409: {"model": BookingError, "description": "Class full or duplicate booking"},
    500: {"model": BookingError, "description": "Transaction failed"}
})
async def book_class(
    booking: BookingRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    1. Phase 1: Deduct balance from MongoDB
    2. Phase 2: Create payment and attendance in ClickHouse
    3. Rollback: If phase 2 fails, refund balance to MongoDB
    """
    
    # Transaction state tracking
    balance_deducted = False
    payment_id = None
    attendance_id = None
    bearer_token = get_bearer_token(request)
    amount_paid = 0.0
    
    try:
        # ============================================================
        # PHASE 0: PRE-VALIDATION (Read-only checks)
        # ============================================================
        
        # Check if class exists
        class_info = select_one("classes", "class_id", str(booking.class_id))
        if not class_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class {booking.class_id} not found"
            )
        
        # Get class details
        class_price = class_info.get("price")
        class_capacity = class_info.get("capacity")
        class_name = class_info.get("name", "Unknown Class")
        
        if class_price is None or class_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class price not set or invalid"
            )
        
        amount_paid = float(class_price)
        
        # Check if member already has an attendance for this class
        existing_attendance_query = f"""
            SELECT count(*) as count 
            FROM attendances 
            WHERE class_id = '{booking.class_id}' 
            AND member_id = '{booking.member_id}'
            FORMAT JSON
        """
        resp = _http_post(existing_attendance_query)
        data = resp.json()
        if data.get("data", [{}])[0].get("count", 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already booked this class"
            )
        
        # Check class capacity
        if class_capacity is not None:
            attendance_count_query = f"""
                SELECT count(*) as count 
                FROM attendances 
                WHERE class_id = '{booking.class_id}'
                FORMAT JSON
            """
            resp = _http_post(attendance_count_query)
            data = resp.json()
            current_attendances = data.get("data", [{}])[0].get("count", 0)
            
            if current_attendances >= class_capacity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Class is full ({current_attendances}/{class_capacity})"
                )
        
        # ============================================================
        # PHASE 1: DEDUCT BALANCE FROM MONGODB (First Write)
        # ============================================================
        
        try:
            balance_result = await deduct_user_balance(
                user_id=booking.member_id,
                amount=amount_paid,
                bearer_token=bearer_token
            )
            balance_deducted = True
            print(f"[TRANSACTION] Balance deducted from user {booking.member_id}: ${amount_paid}")
            
        except InsufficientBalanceError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient balance to book class. Price: ${amount_paid}"
            )
        except BalanceServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"User service unavailable: {str(e)}"
            )
        
        # ============================================================
        # PHASE 2: CREATE PAYMENT RECORD IN CLICKHOUSE
        # ============================================================
        
        payment_data = {
            "payment_id": str(uuid4()),
            "member_id": booking.member_id,
            "class_id": str(booking.class_id),
            "amount": amount_paid,
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        
        try:
            payment_id = insert_one("payments", payment_data)
            if not payment_id:
                payment_id = payment_data["payment_id"]
            print(f"[TRANSACTION] Payment created: {payment_id}")
            
        except Exception as e:
            print(f"[TRANSACTION ERROR] Failed to create payment: {e}")
            raise Exception(f"Failed to create payment record: {str(e)}")
        
        # ============================================================
        # PHASE 3: CREATE ATTENDANCE RECORD IN CLICKHOUSE
        # ============================================================
        
        attendance_data = {
            "event_id": str(uuid4()),
            "class_id": str(booking.class_id),
            "member_id": booking.member_id,
            "timestamp": datetime.utcnow(),
            "status": "confirmed"
        }
        
        try:
            attendance_id = insert_one("attendances", attendance_data)
            if not attendance_id:
                attendance_id = attendance_data["event_id"]
            print(f"[TRANSACTION] Attendance created: {attendance_id}")
            
        except Exception as e:
            print(f"[TRANSACTION ERROR] Failed to create attendance: {e}")
            raise Exception(f"Failed to create attendance record: {str(e)}")
        
        # ============================================================
        # TRANSACTION SUCCESSFUL
        # ============================================================
        
        print(f"[TRANSACTION SUCCESS] User {booking.member_id} booked class {booking.class_id}")
        
        return BookingResponse(
            success=True,
            booking_id=attendance_id,
            payment_id=payment_id,
            attendance_id=attendance_id,
            class_id=str(booking.class_id),
            member_id=booking.member_id,
            amount=amount_paid,
            message=f"Successfully booked '{class_name}' for ${amount_paid}"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise
    
    except Exception as e:
        # ============================================================
        # ROLLBACK: COMPENSATE FOR PARTIAL TRANSACTION
        # ============================================================
        
        print(f"[TRANSACTION ROLLBACK] Error occurred: {str(e)}")
        rollback_errors = []
        
        # Rollback Step 3: Delete attendance if created
        if attendance_id:
            try:
                delete_one("attendances", "event_id", attendance_id)
                print(f"[ROLLBACK] Deleted attendance: {attendance_id}")
            except Exception as rollback_error:
                rollback_errors.append(f"Failed to delete attendance: {rollback_error}")
        
        # Rollback Step 2: Delete payment if created
        if payment_id:
            try:
                delete_one("payments", "payment_id", payment_id)
                print(f"[ROLLBACK] Deleted payment: {payment_id}")
            except Exception as rollback_error:
                rollback_errors.append(f"Failed to delete payment: {rollback_error}")
        
        # Rollback Step 1: Refund balance if deducted
        if balance_deducted:
            try:
                await refund_user_balance(
                    user_id=booking.member_id,
                    amount=amount_paid,
                    bearer_token=bearer_token
                )
                print(f"[ROLLBACK] Refunded balance to user {booking.member_id}: ${amount_paid}")
            except Exception as rollback_error:
                rollback_errors.append(f"CRITICAL: Failed to refund balance: {rollback_error}")
        
        # Construct error message
        error_detail = f"Booking transaction failed: {str(e)}"
        if rollback_errors:
            error_detail += f" | Rollback issues: {'; '.join(rollback_errors)}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/my-bookings")
async def get_my_bookings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get all bookings (attendances) for the current user"""
    import httpx
    import os
    
    # Extract username from current_user
    username = current_user.get("username")
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine username from token"
        )
    
    # Get bearer token from request
    bearer_token = get_bearer_token(request)
    
    # Get user ID from user-service /me endpoint
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/me",
                headers={"Authorization": f"Bearer {bearer_token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                user = response.json()
                user_id = user.get("_id") or user.get("id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User ID not found in user data"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not fetch user information"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )
    
    # Query attendances for this user
    query = f"""
        SELECT 
            a.event_id AS event_id,
            a.class_id AS class_id,
            a.member_id AS member_id,
            a.timestamp AS booking_time,
            a.status AS status,
            c.name AS class_name,
            c.start_time AS start_time,
            c.end_time AS end_time,
            c.price AS price,
            p.payment_id AS payment_id,
            p.amount AS paid_amount,
            p.status AS payment_status
        FROM attendances a
        LEFT JOIN classes c ON a.class_id = c.class_id
        LEFT JOIN payments p ON a.class_id = p.class_id AND a.member_id = p.member_id
        WHERE a.member_id = '{user_id}'
        ORDER BY a.timestamp DESC
        FORMAT JSON
    """
    
    resp = _http_post(query)
    data = resp.json()
    
    return {
        "bookings": data.get("data", []),
        "total_count": len(data.get("data", []))
    }
