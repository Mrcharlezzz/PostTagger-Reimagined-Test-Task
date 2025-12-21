from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.api.domain.models.task_status import TaskStatus


class TaskResultMetadata(BaseModel):
    """Execution metadata for a task result."""

    worker: str | None = None
    queue: str | None = None
    trace_id: str | None = None

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    data: Any | None = Field(default=None, description="Result payload.")
    metadata: TaskResultMetadata | None = None
    expires_at: datetime | None = None
    ttl_seconds: int | None = None
