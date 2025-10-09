from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.application.services import TaskService
from src.api.application.services import ProgressService
from src.api.application.models import StatusDTO  # your Pydantic DTO
from src.setup.api_config import get_api_settings

router = APIRouter(tags=["tasks"])

# Instantiate services once (simple DI)
_settings = get_api_settings()
_task_service = TaskService()
_progress_service = ProgressService()


class EnqueueResponse(BaseModel):
    task_id: str = Field(..., description="Celery task id")


@router.get(
    "/calculate_pi",
    response_model=EnqueueResponse,
    summary="Start π calculation",
    description="Queues an asynchronous task to compute n digits of π. Returns the Celery task id.",
)
def calculate_pi(n: int = Query(..., ge=1, le=_settings.PI_MAX_N,description="Number of digits after decimal")):
    """
    Queues the `compute_pi` task.
    """
    try:
        task_id = _task_service.push_task("compute_pi", {"digits": n})
        return EnqueueResponse(task_id=task_id)
    except ValueError as e:
        # e.g., exceeds pi_max_n as validated in TaskService
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500)


@router.get(
    "/check_progress",
    response_model=StatusDTO,
    summary="Check task progress",
    description=(
        "Poll the status of a Celery task. Returns a JSON with keys:\n"
        "- state: 'PROGRESS' or 'FINISHED'\n"
        "- progress: 0..1 (float)\n"
        "- message: optional error message\n"
        "- result: final value or Null\n\n"
        "Example: {'state':'PROGRESS','progress':0.25,'message':Null, 'result':Null}\n"
    ),
)
def check_progress(task_id: str = Query(..., description="Celery task id to query")):
    """
    Reads the Celery result backend for the given task id and normalizes it into StatusDTO.

    NOTE: Your ProgressService.get_progress currently takes a parameter named `task_name`,
    but it should receive the **task id**. We pass `task_id` here—no behavior change needed.
    """
    try:
        status = _progress_service.get_progress(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500)
