from src.api.application.dtos import StatusDTO  # Backward compatibility
from src.api.domain.models.execution_config import ExecutionConfig
from src.api.domain.models.payloads import ComputePiPayload, DocumentAnalysisPayload, TaskPayload
from src.api.domain.models.task import Task
from src.api.domain.models.task_metadata import TaskMetadata
from src.api.domain.models.task_progress import TaskProgress
from src.api.domain.models.task_result import TaskResult, TaskResultMetadata
from src.api.domain.models.task_state import TaskState
from src.api.domain.models.task_status import TaskStatus
from src.api.domain.models.task_type import TaskType

__all__ = [
    "Task",
    "TaskStatus",
    "TaskProgress",
    "TaskState",
    "TaskType",
    "TaskPayload",
    "DocumentAnalysisPayload",
    "ComputePiPayload",
    "ExecutionConfig",
    "TaskMetadata",
    "TaskResult",
    "TaskResultMetadata",
    "StatusDTO",
]
