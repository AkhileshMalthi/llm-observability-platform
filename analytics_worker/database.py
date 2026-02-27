import clickhouse_connect
import logging
import os
from models import ClickHouseLogRow

logger = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self):
        self.host = os.environ.get("CLICKHOUSE_HOST", "localhost")
        self.port = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
        self.user = os.environ.get("CLICKHOUSE_USER", "default")
        self.password = os.environ.get("CLICKHOUSE_PASSWORD", "")
        self.database = "default"
        self.client = None

    def connect(self):
        logger.info(f"Connecting to ClickHouse at {self.host}:{self.port}...")
        self.client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            database=self.database
        )
        logger.info("Successfully connected to ClickHouse.")
        self.initialize_schema()

    def initialize_schema(self):
        """
        Creates the llm_logs table using the MergeTree engine if it does not already exist.
        The MergeTree engine is ClickHouse's most robust engine for high-volume time-series data.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS llm_logs (
            trace_id UUID,
            timestamp DateTime,
            model String,
            original_prompt String,
            response_content String,
            latency_ms UInt32,
            input_tokens UInt32,
            output_tokens UInt32,
            total_cost_usd Float64
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, trace_id)
        """
        self.client.command(create_table_query)
        logger.info("Verified ClickHouse schema for 'llm_logs' table.")

    def insert_log(self, row: ClickHouseLogRow):
        """
        Inserts a single log row. In a massive production system, we would batch these.
        For ease of development in this project, we stream them individually.
        """
        if not self.client:
            self.connect()

        # The tuple format is strictly required by clickhouse-connect
        data = [[
            row.trace_id,
            row.timestamp,
            row.model,
            row.original_prompt,
            row.response_content,
            row.latency_ms,
            row.input_tokens,
            row.output_tokens,
            row.total_cost_usd
        ]]
        
        column_names = [
            'trace_id', 'timestamp', 'model', 'original_prompt', 'response_content', 
            'latency_ms', 'input_tokens', 'output_tokens', 'total_cost_usd'
        ]
        
        self.client.insert('llm_logs', data, column_names=column_names)
        logger.debug(f"Successfully inserted trace {row.trace_id} into ClickHouse.")
