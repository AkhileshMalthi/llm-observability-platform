import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, AreaChart, Area
} from 'recharts';
import {
  LayoutDashboard, Activity, Terminal, Clock, Layers, CheckCircle2, AlertCircle,
  ChevronRight, RefreshCw, Search
} from 'lucide-react';
import './App.css';

import StatCard from './components/StatCard';
import TraceDetails from './components/TraceDetails';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState({
    totalRequests: 0,
    averageLatencyMs: 0,
    totalCostUsd: 0,
    token_usage_by_model: {},
    status_counts: {}
  });
  const [traces, setTraces] = useState([]);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch logic with 30s polling
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [metricsRes, tracesRes] = await Promise.all([
        fetch('/api/metrics/summary'),
        fetch('/api/traces')
      ]);

      if (metricsRes.ok) {
        setMetrics(await metricsRes.json());
      }
      if (tracesRes.ok) {
        const traceData = await tracesRes.json();
        setTraces(traceData.traces || []);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 30000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  // Derived data
  const trendData = useMemo(() => {
    return [...traces]
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
      .map(t => ({
        time: new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        latency: t.latencyMs || 0,
        cost: t.costUsd || 0
      }));
  }, [traces]);

  const modelChartData = useMemo(() => {
    const counts = traces.reduce((acc, t) => {
      acc[t.model] = (acc[t.model] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [traces]);

  const statusChartData = useMemo(() => {
    const success = traces.filter(t => t.statusCode === 200).length;
    const error = traces.length - success;
    if (traces.length === 0) return [];
    return [
      { name: 'success', value: success },
      { name: 'error', value: error }
    ];
  }, [traces]);

  const COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];

  const successCount = traces.filter(t => t.statusCode === 200).length;
  const successRate = traces.length > 0
    ? ((successCount / traces.length) * 100).toFixed(1)
    : "0.0";

  return (
    <div className="min-h-screen bg-[#090a0c] text-gray-200 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-[#0f1115] flex flex-col sticky top-0 h-screen shrink-0">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20">
            <Layers className="text-white w-5 h-5" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">LLM Traceboard</span>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          <button
            onClick={() => setActiveTab('overview')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === 'overview' ? 'bg-blue-600/10 text-blue-400' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
          >
            <LayoutDashboard className="w-4 h-4" /> Overview
          </button>
          <button
            onClick={() => setActiveTab('traces')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === 'traces' ? 'bg-blue-600/10 text-blue-400' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
          >
            <Activity className="w-4 h-4" /> Traces
          </button>
        </nav>

        <div className="p-4 border-t border-white/5 mt-auto">
          <div className="bg-blue-500/5 rounded-lg p-3 border border-blue-500/10">
            <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">Live Mode</p>
            <p className="text-[11px] text-gray-500">Connected to local BFF telemetry.</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-white/5 bg-[#090a0c]/80 backdrop-blur-md sticky top-0 z-40 px-8 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-white font-medium">
            {activeTab === 'overview' ? 'Platform Overview' : 'Request Traces'}
          </div>
          <div className="flex items-center gap-4">
            {isLoading && <span className="text-xs text-gray-500 animate-pulse">Syncing...</span>}
            <button
              onClick={fetchData}
              className={`p-2 hover:bg-white/5 rounded-lg text-gray-400 transition-all ${isLoading ? 'animate-spin text-blue-400' : ''}`}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </header>

        <div className="p-8 space-y-8 max-w-[1600px] mx-auto w-full">
          {activeTab === 'overview' ? (
            <>
              {/* Stats Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Total Requests" value={(metrics.totalRequests || 0).toLocaleString()} icon={Activity} colorClass="bg-blue-500" />
                <StatCard title="Avg. Latency" value={(metrics.averageLatencyMs || 0).toFixed(0)} unit="ms" icon={Clock} colorClass="bg-purple-500" />
                <StatCard title="Total Cost" value={((metrics.totalCostUsd || 0)).toFixed(4)} unit="USD" icon={Layers} colorClass="bg-amber-500" />
                <StatCard title="Success Rate" value={successRate} unit="%" icon={CheckCircle2} colorClass="bg-green-500" />
              </div>

              {/* Performance Trend Chart */}
              <div className="bg-[#1a1b1e] border border-white/5 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-white font-bold text-lg">Performance Trend</h3>
                  <div className="flex gap-4 text-xs">
                    <div className="flex items-center gap-2 text-blue-400">
                      <div className="w-2 h-2 rounded-full bg-blue-500"></div> Latency (ms)
                    </div>
                  </div>
                </div>
                <div className="h-[240px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData}>
                      <defs>
                        <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff05" />
                      <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 10 }} dy={10} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f1115', border: '1px solid #ffffff10', borderRadius: '8px' }}
                        itemStyle={{ fontSize: '12px' }}
                      />
                      <Area type="monotone" dataKey="latency" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorLatency)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Distribution Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#1a1b1e] border border-white/5 rounded-xl p-6">
                  <h3 className="text-white font-bold text-lg mb-6">Model Usage (Requests)</h3>
                  <div className="h-[240px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={modelChartData} layout="vertical" margin={{ left: 0, right: 20 }}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 11 }} width={120} />
                        <Tooltip cursor={{ fill: '#ffffff05' }} contentStyle={{ backgroundColor: '#0f1115', border: '1px solid #ffffff10', borderRadius: '8px' }} />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                          {modelChartData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-[#1a1b1e] border border-white/5 rounded-xl p-6">
                  <h3 className="text-white font-bold text-lg mb-6">Request Health</h3>
                  <div className="h-[240px] flex items-center justify-center relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={statusChartData} innerRadius={55} outerRadius={75} paddingAngle={8} dataKey="value" stroke="none">
                          <Cell fill="#10b981" />
                          <Cell fill="#ef4444" />
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#0f1115', border: '1px solid #ffffff10', borderRadius: '8px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                      <span className="text-2xl font-bold text-white">{successRate}%</span>
                      <span className="text-[10px] text-gray-500 uppercase tracking-widest">Healthy</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* Traces Tab */
            <div className="bg-[#1a1b1e] border border-white/5 rounded-xl overflow-hidden">
              <div className="p-6 border-b border-white/5 flex items-center justify-between">
                <div><h3 className="text-white font-bold text-lg">Trace Explorer</h3></div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input type="text" placeholder="Search..." className="bg-[#090a0c] border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-xs text-gray-300 w-40" />
                  </div>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-[#141518] text-gray-500 text-[10px] uppercase font-bold tracking-wider">
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Trace ID</th>
                      <th className="px-6 py-4">Model</th>
                      <th className="px-6 py-4">Latency</th>
                      <th className="px-6 py-4">Tokens</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {traces.map((trace) => (
                      <tr key={trace.traceId} onClick={() => setSelectedTrace(trace)} className="hover:bg-white/[0.02] transition-colors cursor-pointer group">
                        <td className="px-6 py-4">{trace.statusCode === 200 ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <AlertCircle className="w-4 h-4 text-red-500" />}</td>
                        <td className="px-6 py-4"><div className="text-sm font-medium text-white font-mono">{trace.traceId.substring(0, 12)}...</div><div className="text-[10px] text-gray-500 mt-0.5">{new Date(trace.timestamp).toLocaleTimeString()}</div></td>
                        <td className="px-6 py-4"><span className="bg-white/5 px-2 py-1 rounded text-[11px] text-gray-400">{trace.model}</span></td>
                        <td className="px-6 py-4 text-sm text-gray-300">{trace.latencyMs}ms</td>
                        <td className="px-6 py-4 text-sm text-gray-400">${trace.costUsd?.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {traces.length === 0 && (
                  <div className="p-8 text-center text-gray-500 text-sm">No traces found.</div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <TraceDetails trace={selectedTrace} onClose={() => setSelectedTrace(null)} />
    </div>
  );
}
