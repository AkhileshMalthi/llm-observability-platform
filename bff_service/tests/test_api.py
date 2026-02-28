import pytest
from fastapi.testclient import TestClient
from main import app, get_db
import logging
from pprint import pformat

logger = logging.getLogger(__name__)

client = TestClient(app)

class MockClickHouseDb:
    def get_summary_metrics(self):
        return {
            "totalRequests": 100,
            "averageLatencyMs": 250.5,
            "totalCostUsd": 0.45
        }

    def get_recent_traces(self, limit: int = 20, offset: int = 0):
        # We simulate the db parameterization to ensure FastAPI routes it correctly
        self.last_limit = limit
        self.last_offset = offset
        return [
            {
                "traceId": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-10-27T10:00:00Z",
                "model": "gpt-4",
                "latencyMs": 150,
                "costUsd": 0.003,
                "statusCode": 200
            }
        ]
        
    def get_total_traces_count(self):
        return 100

@pytest.fixture
def mock_db():
    db = MockClickHouseDb()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()

@pytest.mark.unit
def test_health_endpoint(mock_db):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.unit
def test_metrics_summary_endpoint(mock_db):
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["totalRequests"] == 100
    assert data["averageLatencyMs"] == 250.5
    assert data["totalCostUsd"] == 0.45

@pytest.mark.unit
def test_traces_pagination(mock_db):
    response = client.get("/api/traces?limit=10&offset=20")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 100
    assert len(data["traces"]) == 1
    assert data["traces"][0]["traceId"] == "123e4567-e89b-12d3-a456-426614174000"
    
    # Verify the FastAPI Query parameters successfully propagated to the DB client mock
    assert mock_db.last_limit == 10
    assert mock_db.last_offset == 20

@pytest.mark.e2e
def test_api_e2e(monkeypatch):
    # We must ensure the connection details point to localhost (where ClickHouse is exposed)
    monkeypatch.setenv("CLICKHOUSE_HOST", "localhost")
    monkeypatch.setenv("CLICKHOUSE_PORT", "8123")
    monkeypatch.setenv("CLICKHOUSE_USER", "default")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "password123")
    
    # Test health endpoint
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    logger.info(f"health response: {pformat(health_resp.json())}")
    
    # Test metrics endpoint
    metrics_resp = client.get("/api/metrics/summary")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    logger.info(f"metrics from api: {pformat(metrics_data)}")
    assert "totalRequests" in metrics_data
    
    # Test traces endpoint
    traces_resp = client.get("/api/traces?limit=5")
    assert traces_resp.status_code == 200
    traces_data = traces_resp.json()
    logger.info(f"traces from api: {pformat(traces_data)}")
    assert "traces" in traces_data
    assert "total" in traces_data