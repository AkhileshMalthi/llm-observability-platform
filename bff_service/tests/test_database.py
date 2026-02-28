import os
import pytest
from bff_service.database import ClickHouseDb
import logging
from pprint import pformat

logger = logging.getLogger(__name__)

@pytest.fixture
def db(monkeypatch):
    # Set environment variables so local tests connect to the dockerized ClickHouse correctly
    monkeypatch.setenv("CLICKHOUSE_HOST", "localhost")
    monkeypatch.setenv("CLICKHOUSE_PORT", "8123")
    monkeypatch.setenv("CLICKHOUSE_USER", "default")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "password123")
    return ClickHouseDb()

@pytest.mark.e2e
def test_clickhouse_connection_and_metrics(db: ClickHouseDb):
    try:
        # Check if we can get summary metrics
        metrics = db.get_summary_metrics()
        logger.info(f"metrics from db: {pformat(metrics)}")

        assert "totalRequests" in metrics
        assert "averageLatencyMs" in metrics
        assert "totalCostUsd" in metrics
        
        # Check if we can get recent traces
        traces = db.get_recent_traces(limit=5)
        logger.info(f"traces from db: {pformat(traces)}")

        assert isinstance(traces, list)
        
        # Check count
        count = db.get_total_traces_count()
        logger.info(f"count from db: {count}")

        assert isinstance(count, int)
        
    except Exception as e:
        pytest.fail(f"Database operation failed with error: {e}")
