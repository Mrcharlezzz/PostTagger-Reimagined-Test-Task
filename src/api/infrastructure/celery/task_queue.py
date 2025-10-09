from src.api.infrastructure.celery.app import celery_app

def enqueue(task_name : str, payload: dict) -> str:
    """
    Enqueue a task in the broker.
    """
    async_result = celery_app.send_task(task_name, args=[payload])
    return async_result.id
