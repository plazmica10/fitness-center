"""
Placeholder client for future Member Service.
For now, calls are no-ops to keep the transaction shape without touching another DB.
"""
import asyncio
from typing import Dict, Any


class MemberServiceClient:
    async def reserve_slot(self, member_id: str, class_id: str) -> Dict[str, Any]:
        # TODO: implement real call when member service is available
        await asyncio.sleep(0)  # keep async signature
        return {}

    async def cancel_reservation(self, member_id: str, reservation_id: str) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {}

    async def record_payment(self, member_id: str, amount: float, class_id: str) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {}

    async def refund_payment(self, member_id: str, payment_id: str) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {}


member_service_client = MemberServiceClient()
