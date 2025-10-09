from celery.result import AsyncResult

from src.api.application.models import StatusDTO
from src.api.infrastructure.celery.app import celery_app
from src.api.infrastructure.mappers import to_status_dto

def get_status(task_id: str) -> StatusDTO:
    result = AsyncResult(task_id, app=celery_app)
    return to_status_dto(result)