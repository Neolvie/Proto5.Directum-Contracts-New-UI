from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app
from src.services.llm_client import StubLLMClient


def test_upload_and_chat(tmp_path: Path) -> None:
    app.state.llm_client = StubLLMClient()
    app.state.rating_log_path = tmp_path / "ratings.jsonl"
    client = TestClient(app)

    sample = tmp_path / "sample.md"
    sample.write_text("Пример документа", encoding="utf-8")

    with sample.open("rb") as handle:
        response = client.post(
            "/api/upload",
            params={"session_id": "session-123"},
            files={"files": ("sample.md", handle, "text/markdown")},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"]

    chat_response = client.post(
        "/api/chat",
        json={
            "session_id": "session-123",
            "message": "Проверь документ",
            "role": "legal",
            "mode": "short",
        },
    )
    assert chat_response.status_code == 200
    assert "Тестовый ответ" in chat_response.json()["answer"]

    rating_response = client.post(
        "/api/rating",
        json={
            "session_id": "session-123",
            "message_id": "msg-1",
            "rating": "up",
            "role": "legal",
            "mode": "short",
            "question": "Вопрос",
        },
    )
    assert rating_response.status_code == 200
