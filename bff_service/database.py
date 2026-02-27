import clickhouse_connect
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ClickHouseDb:
    def __init__(self):
        self.host = os.environ.get("CLICKHOUSE_HOST", "localhost")
        self.port = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
        self.user = os.environ.get("CLICKHOUSE_USER", "default")
        self.password = os.environ.get("CLICKHOUSE_PASSWORD", "")
        self.database = "default"
        self.client = None

    def connect(self):
        """Lazy connects to ClickHouse."""
        if not self.client:
            logger.info(f"Connecting to ClickHouse at {self.host}:{self.port}...")
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=self.database
            )

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Executes a fast aggregation query over the entire llm_logs table.
        Returns totalRequests, averageLatencyMs, totalCostUsd.
        """
        self.connect()
        query = """
            SELECT 
                count() as total_reqs, 
                avg(latency_ms) as avg_lat, 
                sum(total_cost_usd) as total_cost 
            FROM llm_logs
        """
        result = self.client.query(query)
        row = result.result_rows[0]
        
        return {
            "totalRequests": int(row[0]) if row[0] is not None else 0,
            "averageLatencyMs": float(row[1]) if row[1] is not None else 0.0,
            "totalCostUsd": float(row[2]) if row[2] is not None else 0.0
        }

    def get_recent_traces(self, limit: int = 20, offset: int = 0) -> list:
        """
        Fetches a paginated list of traces sorted by reverse chronological order.
        Uses parameterized parameters to prevent SQL injection.
        """
        self.connect()
        query = """
            SELECT trace_id, timestamp, model, latency_ms, total_cost_usd 
            FROM llm_logs 
            ORDER BY timestamp DESC 
            LIMIT {limit:UInt32} OFFSET {offset:UInt32}
        """
        parameters = {"limit": limit, "offset": offset}
        result = self.client.query(query, parameters=parameters)
        
        traces = []
        for row in result.result_rows:
            traces.append({
                "traceId": str(row[0]),
                # Format to ISO 8601 string for frontend JSON serialization
                "timestamp": row[1].isoformat() + "Z" if row[1] else "",
                "model": row[2],
                "latencyMs": int(row[3]),
                "costUsd": float(row[4]),
                "statusCode": 200 # Worker only logs successful LLM 200 responses currently
            })
        return traces

    def get_total_traces_count(self) -> int:
        """
        Returns the absolute count of traces for pagination metadata.
        """
        self.connect()
        query = "SELECT count() FROM llm_logs"
        result = self.client.query(query)
        return int(result.result_rows[0][0])

# Global instance for FastAPI dependency injection
db_client = ClickHouseDb()

def get_db() -> ClickHouseDb:
    return db_client
