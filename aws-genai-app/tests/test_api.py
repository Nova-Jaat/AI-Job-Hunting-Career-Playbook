import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ready_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

@patch("app.routes.rag_pipeline.query")
def test_chat_endpoint_success(mock_query):
    mock_query.return_value = {
        "answer": "Bedrock is a managed service for foundation models.",
        "sources": [{"doc_id": "doc_1", "source": "aws_docs.pdf", "score": 0.89, "snippet": "..."}],
        "usage": {"inputTokens": 120, "outputTokens": 45},
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    }

    payload = {
        "question": "What is Amazon Bedrock?",
        "history": [],
        "top_k": 3,
        "temperature": 0.1,
        "use_hybrid": True
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["sources"]) == 1
    assert data["model"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
