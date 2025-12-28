import time

from src.app.infrastructure.celery.app import celery_app
from src.app.domain.models.task_progress import TaskProgress
from src.app.domain.models.task_state import TaskState
from src.app.domain.models.task_status import TaskStatus
from src.app.worker.reporter import TaskReporter


def _simulate_steps(reporter: TaskReporter, steps: int, sleep: float) -> None:
    for idx in range(steps):
        time.sleep(sleep)
        progress = (idx + 1) / steps
        status = TaskStatus(
            state=TaskState.RUNNING,
            progress=TaskProgress(current=idx + 1, total=steps, percentage=progress),
        )
        reporter.report_status(status)


@celery_app.task(name="document_analysis", bind=True)
def document_analysis(self, payload: dict) -> dict:
    """
    Dummy document analysis task.
    """
    reporter = TaskReporter(self.request.id)
    _simulate_steps(reporter, steps=5, sleep=0.1)
    result = {
        "task_id": self.request.id,
        "task_type": payload.get("task_type"),
        "payload": payload.get("payload"),
        "analysis": "documents analyzed",
    }
    reporter.report_result(result)
    return result
