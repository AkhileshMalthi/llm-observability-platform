import React from 'react';

export default function TracesTable({ traces }) {
    if (!traces || traces.length === 0) {
        return <div className="loading-container">No traces available yet.</div>;
    }

    return (
        <div className="table-container" data-testid="traces-table">
            <div className="table-header">
                <h2>Recent Traces</h2>
                <span className="text-secondary">{traces.length} traces shown</span>
            </div>
            <table className="styled-table">
                <thead>
                    <tr>
                        <th>Trace ID</th>
                        <th>Timestamp</th>
                        <th>Model</th>
                        <th>Latency (ms)</th>
                        <th>Cost (USD)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {traces.map((trace) => (
                        <tr key={trace.traceId} data-testid="trace-row">
                            <td data-testid="trace-id-cell">
                                <span style={{ fontFamily: 'monospace', color: 'var(--accent-primary)' }}>
                                    {trace.traceId.split('-')[0]}...
                                </span>
                            </td>
                            <td>{new Date(trace.timestamp).toLocaleString()}</td>
                            <td>{trace.model}</td>
                            <td style={{ color: trace.latencyMs > 2000 ? 'var(--error)' : 'inherit' }}>
                                {trace.latencyMs}ms
                            </td>
                            <td>${trace.costUsd.toFixed(6)}</td>
                            <td>
                                <span className={`status-badge ${trace.statusCode >= 400 ? 'error' : ''}`}>
                                    {trace.statusCode}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
