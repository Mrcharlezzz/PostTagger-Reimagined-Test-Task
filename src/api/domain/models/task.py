from datetime import datetime

from pydantic import BaseModel

from src.api.domain.models.payloads import TaskPayload
from src.api.domain.models.task_status import TaskStatus


class Task(BaseModel):
    id: str
    payload: TaskPayload  # can hold any subclass
    result: dict | None = None
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
