import pytest
from fastapi.testclient import TestClient
from main import app, get_db

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

mock_db = MockClickHouseDb()

# Override the database dependency for tests
app.dependency_overrides[get_db] = lambda: mock_db

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_metrics_summary_endpoint():
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["totalRequests"] == 100
    assert data["averageLatencyMs"] == 250.5
    assert data["totalCostUsd"] == 0.45

def test_traces_pagination():
    response = client.get("/api/traces?limit=10&offset=20")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 100
    assert len(data["traces"]) == 1
    assert data["traces"][0]["traceId"] == "123e4567-e89b-12d3-a456-426614174000"
    
    # Verify the FastAPI Query parameters successfully propagated to the DB client mock
    assert mock_db.last_limit == 10
    assert mock_db.last_offset == 20
