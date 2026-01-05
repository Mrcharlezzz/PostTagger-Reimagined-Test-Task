from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.application.handlers import TaskEventHandler
from src.app.domain.events.task_event import TaskEvent
from src.app.domain.models.task_progress import TaskProgress
from src.app.domain.models.task_state import TaskState
from src.app.domain.models.task_status import TaskStatus
from src.app.domain.repositories import StorageRepository
from src.app.presentation.websockets import (
    WebSocketStatusBroadcaster,
    connection_manager,
    router as ws_router,
)


class StubStorage(StorageRepository):
    async def create_task(self, user_id: str, task):  # pragma: no cover - not used
        raise NotImplementedError

    async def get_task(self, user_id: str, task_id: str):  # pragma: no cover - not used
        raise NotImplementedError

    async def get_status(self, user_id: str, task_id: str):  # pragma: no cover - not used
        raise NotImplementedError

    async def get_result(self, user_id: str, task_id: str):  # pragma: no cover - not used
        raise NotImplementedError

    async def list_tasks(self, user_id: str, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError

    async def update_task_status(self, task_id: str, status: TaskStatus, metadata=None) -> None:
        return None

    async def set_task_result(self, task_id: str, result, finished_at=None) -> None:
        return None


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(ws_router)
    return app


def test_websocket_receives_status_and_chunks() -> None:
    connection_manager._connections.clear()
    app = _build_app()
    broadcaster = WebSocketStatusBroadcaster(connection_manager)
    handler = TaskEventHandler(storage=StubStorage(), broadcaster=broadcaster)
    task_id = "task-pi-1"

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/tasks/{task_id}") as ws:
            status = TaskStatus(
                state=TaskState.RUNNING,
                progress=TaskProgress(current=1, total=3, percentage=1 / 3),
            )
            status_event = TaskEvent.status(task_id, status)
            chunk_event = TaskEvent.result_chunk(task_id, "0", {"digit": "3"}, is_last=False)

            client.portal.call(handler.handle_status_event, status_event)
            client.portal.call(handler.handle_result_chunk_event, chunk_event)

            status_msg = ws.receive_json()
            chunk_msg = ws.receive_json()

    assert status_msg["type"] == status_event.type.value
    assert status_msg["task_id"] == task_id
    assert status_msg["payload"] == status_event.payload

    assert chunk_msg["type"] == chunk_event.type.value
    assert chunk_msg["task_id"] == task_id
    assert chunk_msg["payload"] == chunk_event.payload
