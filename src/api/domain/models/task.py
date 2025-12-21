from pydantic import BaseModel, Field

from src.api.domain.models.execution_config import ExecutionConfig
from src.api.domain.models.payloads import TaskPayload
from src.api.domain.models.task_metadata import TaskMetadata
from src.api.domain.models.task_status import TaskStatus
from src.api.domain.models.task_type import TaskType


class Task(BaseModel):
    id: str | None = Field(default=None, description="Unique task identifier.")
    task_type: TaskType = Field(description="Type of task being executed.")
    payload: TaskPayload = Field(description="Task-specific payload data.")
    result: dict | None = Field(
        default=None, description="Raw result payload, if available."
    )
    status: TaskStatus = Field(description="Current status information.")
    metadata: TaskMetadata = Field(description="Lifecycle metadata for the task.")
    execution: ExecutionConfig | None = Field(
        default=None, description="Execution configuration overrides."
    )
