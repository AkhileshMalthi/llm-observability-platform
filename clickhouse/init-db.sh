#!/bin/bash
set -e

clickhouse-client -n <<-EOSQL
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
    ORDER BY timestamp;
EOSQL