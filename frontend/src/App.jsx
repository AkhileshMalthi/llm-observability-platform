import { useState, useEffect } from 'react';
import MetricsCard from './components/MetricsCard';
import TracesTable from './components/TracesTable';
import './index.css';

// The BFF container is accessible at the host's port map if run locally,
// but inside docker-compose it's often easiest to target localhost mappings since React is rendered browser-side.
const API_BASE_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:8001';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [tracesData, setTracesData] = useState({ traces: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [metricsRes, tracesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/metrics/summary`),
        fetch(`${API_BASE_URL}/api/traces?limit=20&offset=0`)
      ]);

      if (!metricsRes.ok || !tracesRes.ok) {
        throw new Error('Failed to fetch telemetry payload from BFF');
      }

      setMetrics(await metricsRes.json());
      setTracesData(await tracesRes.json());
    } catch (err) {
      console.error(err);
      setError('Unable to connect to the Analytics Backend (BFF Service).');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Auto refresh every 10 seconds to simulate real-time observability
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>Safety & Observability Control Plane</h1>
        <p>Real-time analytics & telemetry logs across all LLM inference endpoints</p>
      </header>

      {error ? (
        <div className="error-container">
          <h3>Connection Error</h3>
          <p>{error}</p>
        </div>
      ) : loading && !metrics ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <h2>Fetching Telemetry...</h2>
        </div>
      ) : (
        <>
          <div className="metrics-grid">
            <MetricsCard
              title="Total Requests"
              value={metrics?.totalRequests || 0}
              testId="metric-total-requests"
            />
            <MetricsCard
              title="Avg Latency"
              value={Math.round(metrics?.averageLatencyMs || 0)}
              suffix="ms"
              testId="metric-avg-latency"
            />
            <MetricsCard
              title="Total Cost Accumulation"
              value={(metrics?.totalCostUsd || 0).toFixed(4)}
              prefix="$"
              testId="metric-total-cost"
            />
          </div>

          <TracesTable traces={tracesData.traces} />
        </>
      )}
    </div>
  );
}

export default App;
