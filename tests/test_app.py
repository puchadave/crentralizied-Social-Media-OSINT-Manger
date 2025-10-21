"""Integration tests for the FastAPI application."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _generate_content() -> dict:
    response = client.post(
        "/v1/content/generate",
        json={
            "topic": "KI im Marketing",
            "platform": "LinkedIn",
            "tone": "fachlich",
            "language": "de",
            "format": "post",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_content_generation_fallback() -> None:
    payload = _generate_content()
    assert payload["metadata"]["used_fallback"] is True
    assert "KI im Marketing" in payload["content"]["body"]
    assert payload["content"]["hashtags"]


def test_schedule_post() -> None:
    content_payload = _generate_content()
    scheduled_time = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
    response = client.post(
        "/v1/posts/schedule",
        json={
            "content": content_payload["content"],
            "scheduled_time": scheduled_time,
            "platforms": ["LinkedIn", "Twitter"],
            "campaign": "launch",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "scheduled"
    assert set(data["platforms"]) == {"LinkedIn", "Twitter"}


def test_monitoring_ingest_and_reports() -> None:
    post_id = "post-123"
    now = datetime.now(tz=timezone.utc).isoformat()
    response = client.post(
        "/v1/monitoring/interactions",
        json={
            "post_id": post_id,
            "platform": "LinkedIn",
            "interactions": [
                {
                    "user_id": "user-a",
                    "user_display_name": "Analyst A",
                    "interaction_type": "comment",
                    "content": "Spannender Beitrag!",
                    "timestamp": now,
                    "follower_count": 1200,
                },
                {
                    "user_id": "user-b",
                    "interaction_type": "repost",
                    "timestamp": now,
                    "in_reply_to": "user-a",
                    "follower_count": 800,
                },
            ],
        },
    )
    assert response.status_code == 201
    summary = response.json()
    assert summary["total_interactions"] == 2
    assert summary["unique_users"] == 2
    assert summary["estimated_reach"] >= 2

    summary_response = client.get(f"/v1/monitoring/posts/{post_id}/summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["comments"] == 1

    network_response = client.get(f"/v1/monitoring/posts/{post_id}/network")
    assert network_response.status_code == 200
    network = network_response.json()
    assert any(node["type"] == "post" for node in network["nodes"])
    assert len(network["edges"]) >= 2
