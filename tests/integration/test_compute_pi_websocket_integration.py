from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError, TimeoutError

import inject

from src.app.application.handlers import TaskEventHandler
from src.app.domain.events.task_event import EventType
from src.app.domain.models.task_status import TaskStatus
from src.app.domain.repositories import StorageRepository, TaskEventPublisherRepository
from src.app.infrastructure.streams.client import StreamsClient, SyncStreamsClient
from src.app.infrastructure.streams.consumer import StreamsConsumer
from src.app.infrastructure.streams.publisher import StreamsSyncPublisher
from src.app.infrastructure.streams.router import EventRouter
from src.app.presentation.websockets import (
    WebSocketStatusBroadcaster,
    connection_manager,
    router as ws_router,
)
import importlib
from src.setup.stream_config import StreamSettings


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

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        metadata=None,
    ) -> None:
        return None

    async def set_task_result(self, task_id: str, result, finished_at=None) -> None:
        return None


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(ws_router)
    return app


async def _start_consumer(consumer: StreamsConsumer, stop_event) -> None:
    await consumer.start()
    await stop_event.wait()
    await consumer.stop()


def test_compute_pi_streams_status_and_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    redis_url = StreamSettings().REDIS_URL
    if not redis_url:
        pytest.skip("REDIS_URL not set; skipping compute_pi websocket integration test.")

    stream_name = f"test:events:{uuid4().hex}"
    group = f"test-group:{uuid4().hex}"
    consumer_name = f"test-consumer:{uuid4().hex}"
    task_id = f"task-{uuid4().hex}"

    sync_client = SyncStreamsClient(redis_url)
    try:
        sync_client.redis.ping()
    except (ConnectionError, TimeoutError):
        sync_client.close()
        pytest.skip(f"Cannot reach Redis at {redis_url}; skipping integration test.")

    streams_client = StreamsClient(redis_url)
    publisher = StreamsSyncPublisher(sync_client, stream_name)

    def fake_instance(interface: object) -> object:
        if interface is TaskEventPublisherRepository:
            return publisher
        raise RuntimeError(f"Unexpected dependency request: {interface}")

    monkeypatch.setattr(inject, "instance", fake_instance)
    compute_pi_module = importlib.import_module("src.app.worker.tasks.compute_pi")
    monkeypatch.setattr(compute_pi_module._settings, "SLEEP_PER_DIGIT_SEC", 0)

    broadcaster = WebSocketStatusBroadcaster(connection_manager)
    handler = TaskEventHandler(storage=StubStorage(), broadcaster=broadcaster)
    router = EventRouter()
    router.register(EventType.TASK_STATUS, handler.handle_status_event)
    router.register(EventType.TASK_RESULT_CHUNK, handler.handle_result_chunk_event)
    router.register(EventType.TASK_RESULT, handler.handle_result_event)

    consumer = StreamsConsumer(
        streams_client,
        stream=stream_name,
        group=group,
        consumer_name=consumer_name,
        router=router,
        block_ms=50,
        count=10,
        reclaim_pending=False,
        reclaim_idle_ms=1000,
    )

    app = _build_app()
    connection_manager._connections.clear()

    payload = {"payload": {"digits": 3}}
    expected_pi = compute_pi_module.get_pi(payload["payload"]["digits"])
    expected_count = len(expected_pi)

    with TestClient(app) as client:
        stop_event = client.portal.call(lambda: asyncio.Event())
        client.portal.start_task_soon(_start_consumer, consumer, stop_event)
        try:
            with client.websocket_connect(f"/ws/tasks/{task_id}") as ws:
                compute_pi_module.compute_pi.push_request(args=(payload,), kwargs={})
                try:
                    compute_pi_module.compute_pi.request.id = task_id
                    compute_pi_module.compute_pi.run(payload)
                finally:
                    compute_pi_module.compute_pi.pop_request()

                statuses: list[dict[str, object]] = []
                chunks: list[dict[str, object]] = []
                chunk_done = False
                max_messages = expected_count + 5
                for _ in range(max_messages):
                    message = ws.receive_json()
                    if message["type"] == EventType.TASK_STATUS.value:
                        statuses.append(message)
                    elif message["type"] == EventType.TASK_RESULT_CHUNK.value:
                        chunks.append(message)
                        if message["payload"]["is_last"] is True:
                            chunk_done = True
                    if chunk_done and len(statuses) >= expected_count:
                        break
        finally:
            client.portal.call(stop_event.set)
            client.portal.call(consumer.stop)
            client.portal.call(streams_client.close)
            sync_client.redis.delete(stream_name)
            sync_client.close()

    assert len(statuses) == expected_count
    data_chunks = [chunk for chunk in chunks if chunk["payload"]["data"]]
    assert len(data_chunks) == expected_count

    data_chunks.sort(key=lambda item: int(item["payload"]["chunk_id"]))
    received_digits = [
        chunk["payload"]["data"][0]
        for chunk in data_chunks
    ]
    assert received_digits == list(expected_pi)
    assert any(chunk["payload"]["is_last"] is True for chunk in chunks)
