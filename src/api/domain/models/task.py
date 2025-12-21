from pydantic import BaseModel

from src.api.domain.models.execution_config import ExecutionConfig
from src.api.domain.models.payloads import TaskPayload
from src.api.domain.models.task_metadata import TaskMetadata
from src.api.domain.models.task_status import TaskStatus
from src.api.domain.models.task_type import TaskType


class Task(BaseModel):
    id: str | None = None
    task_type: TaskType
    payload: TaskPayload  # can hold any subclass
    result: dict | None = None
    status: TaskStatus
    metadata: TaskMetadata
    execution: ExecutionConfig | None = None
