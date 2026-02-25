#!/bin/bash
set -e

clickhouse-client --host localhost --query "
    CREATE DATABASE IF NOT EXISTS default;

    CREATE TABLE IF NOT EXISTS default.llm_logs (
        trace_id UUID,
        timestamp DateTime,
        model String,
        original_prompt String,
        processed_prompt String,
        response_content String,
        latency_ms UInt32,
        input_tokens UInt32,
        output_tokens UInt32,
        total_cost_usd Float64,
        pii_redacted UInt8,
        injection_detected UInt8
    ) ENGINE = MergeTree()
    ORDER BY timestamp;
"

echo "ClickHouse initialized: llm_logs table created."