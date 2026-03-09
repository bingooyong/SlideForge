"""FastAPI 端点集成测试。"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient。"""
    return TestClient(app)


@pytest.fixture
def client_with_fresh_store(fresh_task_store):
    """使用独立 task_store 的 client，覆盖 app 的 get_task_store。"""
    from app.dependencies import get_task_store

    def override():
        return fresh_task_store

    app.dependency_overrides[get_task_store] = override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    """GET /health 应返回 200。"""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_upload_returns_202_with_task_id(
    client: TestClient,
    minimal_pdf_path: Path,
) -> None:
    """POST /upload 应返回 202，且 body 含 taskId、filename、pageCount、status。"""
    with open(minimal_pdf_path, "rb") as f:
        r = client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"mode": "standard", "aspectRatio": "16:9"},
        )
    assert r.status_code == 202
    data = r.json()
    assert "taskId" in data
    assert data.get("filename") == "test.pdf"
    assert data.get("pageCount") == 1
    assert data.get("status") in ("queued", "processing")


def test_get_task_returns_404_for_unknown(client: TestClient) -> None:
    """GET /tasks/{taskId} 对不存在的任务应返回 404。"""
    r = client.get("/api/v1/tasks/unknown-task-id")
    assert r.status_code == 404


def test_get_task_returns_200_for_existing(
    client_with_fresh_store: TestClient,
    fresh_task_store,
) -> None:
    """GET /tasks/{taskId} 对存在的任务应返回 200 及任务状态。"""
    from app.core.task_store import TaskStatus

    fresh_task_store.create_task(
        TaskStatus(
            taskId="task-123",
            filename="a.pdf",
            status="processing",
            progress=50,
            currentPage=0,
            totalPages=2,
            stage="processing",
            failedPages=[],
        )
    )
    r = client_with_fresh_store.get("/api/v1/tasks/task-123")
    assert r.status_code == 200
    assert r.json()["taskId"] == "task-123"
    assert r.json()["status"] == "processing"


def test_export_returns_404_for_unknown(client: TestClient) -> None:
    """GET /export/{taskId} 对不存在的任务应返回 404。"""
    r = client.get("/api/v1/export/unknown-task-id")
    assert r.status_code == 404


def test_export_returns_202_when_not_ready(
    client_with_fresh_store: TestClient,
    fresh_task_store,
) -> None:
    """GET /export/{taskId} 对未完成的任务应返回 202。"""
    from app.core.task_store import TaskStatus

    fresh_task_store.create_task(
        TaskStatus(
            taskId="task-queued",
            filename="a.pdf",
            status="queued",
            progress=0,
            stage="uploading",
            totalPages=1,
            failedPages=[],
        )
    )
    r = client_with_fresh_store.get("/api/v1/export/task-queued")
    assert r.status_code == 202


def test_export_returns_200_with_pptx_file(
    client_with_fresh_store: TestClient,
    completed_task_with_export: tuple[str, Path],
) -> None:
    """GET /export/{taskId} 对已完成任务应返回 200 及 PPTX 流；Content-Type 与文件名正确。"""
    task_id, _ = completed_task_with_export
    r = client_with_fresh_store.get(f"/api/v1/export/{task_id}")
    assert r.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        in r.headers.get("content-type", "")
    )
    assert "Content-Disposition" in r.headers
    assert "test.pptx" in r.headers.get("Content-Disposition", "")
    assert len(r.content) > 0
