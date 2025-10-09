from celery.result import AsyncResult

from src.api.application.models import StatusDTO
from pydantic import ValidationError

def to_status_dto(result : AsyncResult) -> StatusDTO:
    info = result.info or {}
    try:
        if result.failed():
            return StatusDTO(
                task_id=result.id,
                state="FAILURE",
                percent=None,
                message=info.get("message"),
                result=None,
            )

        return StatusDTO(
            task_id=result.id,
            state=result.state,
            percent=info.get("percent"),
            message=info.get("message"),
            result=result.result if result.successful() else None,
        )

    except ValidationError as e:
        # fallback: mark as failure with error message
        return StatusDTO(
            task_id=result.id,
            state="FAILURE",
            percent=None,
            message=f"Mapping error: {e.errors()}",
            result=None,
        )