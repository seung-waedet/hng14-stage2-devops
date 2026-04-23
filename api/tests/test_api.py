import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    with patch('main.get_redis_client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

def test_health_check_healthy(mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check_unhealthy(mock_redis):
    mock_redis.ping.side_effect = Exception("Connection refused")
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"

def test_create_job_success(mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    mock_redis.hget.return_value = "queued"

    response = client.post("/jobs")
    assert response.status_code == 200
    assert "job_id" in response.json()
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()

def test_get_job_found(mock_redis):
    mock_redis.hget.return_value = "completed"
    test_job_id = "test-123"

    response = client.get(f"/jobs/{test_job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == test_job_id
    assert response.json()["status"] == "completed"

def test_get_job_not_found(mock_redis):
    mock_redis.hget.return_value = None
    test_job_id = "nonexistent-job"

    response = client.get(f"/jobs/{test_job_id}")
    assert response.status_code == 200
    assert response.json()["error"] == "not found"