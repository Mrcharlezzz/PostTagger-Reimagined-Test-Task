from src.api.application.models import StatusDTO
from src.api.infrastructure.celery.task_queue import enqueue
from src.api.infrastructure.celery.task_status import get_status

class ProgressService:
    def get_progress(self, task_name: str) -> StatusDTO:
        status = get_status(task_name)
        return status

class TaskService:
    def push_task(self, task_name, payload: dict) -> str:
        task_id = enqueue(task_name, payload)
        return task_id