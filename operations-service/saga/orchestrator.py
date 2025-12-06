"""
Simple Saga orchestrator for coordinating multi-step operations.
This is in-process and keeps state in memory.
"""
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class TransactionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    name: str
    execute: Callable
    compensate: Callable
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None


@dataclass
class SagaTransaction:
    transaction_id: str
    status: TransactionStatus
    steps: List[SagaStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class SagaOrchestrator:
    def __init__(self) -> None:
        self.active: Dict[str, SagaTransaction] = {}

    def create_transaction(self) -> str:
        tid = str(uuid.uuid4())
        self.active[tid] = SagaTransaction(transaction_id=tid, status=TransactionStatus.PENDING)
        return tid

    def add_step(self, transaction_id: str, name: str, execute: Callable, compensate: Callable) -> None:
        if transaction_id not in self.active:
            raise ValueError("Transaction not found")
        tx = self.active[transaction_id]
        if tx.status != TransactionStatus.PENDING:
            raise ValueError("Cannot add steps after execution starts")
        tx.steps.append(SagaStep(name=name, execute=execute, compensate=compensate))

    async def execute(self, transaction_id: str) -> Dict[str, Any]:
        if transaction_id not in self.active:
            raise ValueError("Transaction not found")
        tx = self.active[transaction_id]
        tx.status = TransactionStatus.IN_PROGRESS
        executed: List[SagaStep] = []
        try:
            for step in tx.steps:
                try:
                    step.result = await step.execute()
                    step.status = StepStatus.COMPLETED
                    executed.append(step)
                except Exception as exc:  # pragma: no cover - simple pass-through
                    step.status = StepStatus.FAILED
                    step.error = str(exc)
                    raise
            tx.status = TransactionStatus.COMPLETED
            tx.completed_at = datetime.now(timezone.utc)
            return {
                "transaction_id": transaction_id,
                "status": tx.status.value,
                "steps": [s.status.value for s in tx.steps],
                "results": [s.result for s in tx.steps],
            }
        except Exception as exc:
            tx.status = TransactionStatus.COMPENSATING
            tx.error = str(exc)
            compensation = await self._compensate(executed)
            tx.status = TransactionStatus.COMPENSATED
            tx.completed_at = datetime.now(timezone.utc)
            return {
                "transaction_id": transaction_id,
                "status": tx.status.value,
                "error": str(exc),
                "compensation": compensation,
            }

    async def _compensate(self, executed: List[SagaStep]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for step in reversed(executed):
            try:
                res = await step.compensate()
                step.status = StepStatus.COMPENSATED
                results.append({"step": step.name, "status": step.status.value, "result": res})
            except Exception as exc:  # pragma: no cover - best-effort
                results.append({"step": step.name, "status": "compensation_failed", "error": str(exc)})
        return results

    def get_status(self, transaction_id: str) -> Dict[str, Any]:
        if transaction_id not in self.active:
            raise ValueError("Transaction not found")
        tx = self.active[transaction_id]
        return {
            "transaction_id": transaction_id,
            "status": tx.status.value,
            "created_at": tx.created_at.isoformat(),
            "completed_at": tx.completed_at.isoformat() if tx.completed_at else None,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "error": s.error,
                }
                for s in tx.steps
            ],
            "error": tx.error,
        }


saga_orchestrator = SagaOrchestrator()
