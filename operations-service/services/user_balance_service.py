"""
User Balance Service Client
Handles communication with user-service for balance operations
"""
import os
import httpx
from typing import Optional, Dict, Any

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")


class BalanceServiceError(Exception):
    """Raised when balance service operations fail"""
    pass


class InsufficientBalanceError(BalanceServiceError):
    """Raised when user has insufficient balance"""
    pass


async def get_user_balance(user_id: str, bearer_token: str) -> float:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{USER_SERVICE_URL}/users/{user_id}/balance",
                headers=headers,
                timeout=5.0
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("balance", 0.0)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise BalanceServiceError(f"User {user_id} not found")
        raise BalanceServiceError(f"Failed to get balance: {e.response.text}")
    except Exception as e:
        raise BalanceServiceError(f"Balance service error: {str(e)}")


async def deduct_user_balance(user_id: str, amount: float, bearer_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    payload = {"amount": amount}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{USER_SERVICE_URL}/users/{user_id}/balance/deduct",
                headers=headers,
                json=payload,
                timeout=5.0
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 402:  # Payment Required
            raise InsufficientBalanceError(f"Insufficient balance for user {user_id}")
        elif e.response.status_code == 404:
            raise BalanceServiceError(f"User {user_id} not found")
        raise BalanceServiceError(f"Failed to deduct balance: {e.response.text}")
    except Exception as e:
        raise BalanceServiceError(f"Balance service error: {str(e)}")


async def refund_user_balance(user_id: str, amount: float, bearer_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    payload = {"amount": amount}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{USER_SERVICE_URL}/users/{user_id}/balance/add",
                headers=headers,
                json=payload,
                timeout=5.0
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise BalanceServiceError(f"User {user_id} not found")
        raise BalanceServiceError(f"Failed to refund balance: {e.response.text}")
    except Exception as e:
        raise BalanceServiceError(f"Balance service error: {str(e)}")
