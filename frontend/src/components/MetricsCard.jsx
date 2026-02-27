import React from 'react';

export default function MetricsCard({ title, value, testId, prefix = '', suffix = '' }) {
  return (
    <div className="metric-card">
      <div className="metric-title">{title}</div>
      <div className="metric-value" data-testid={testId}>
        {prefix}{value}{suffix}
      </div>
    </div>
  );
}
