# src/api/application/status_dto.py
from pydantic import BaseModel, Field
from typing import Optional, Any

class StatusDTO(BaseModel):
    """
    Represents the status of a Celery task.
    """
    task_id: str = Field(..., description="Unique identifier of the task")
    state: str = Field(..., description="Celery task state: PENDING, STARTED, PROGRESS, SUCCESS, FAILURE")
    percent: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage if available")
    message: Optional[str] = Field(None, description="Optional progress or error message")
    result: Optional[Any] = Field(None, description="Task result data if state=SUCCESS")