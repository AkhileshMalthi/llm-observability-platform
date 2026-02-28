import React from 'react';
import { ChevronRight, Terminal, Activity } from 'lucide-react';

export default function TraceDetails({ trace, onClose }) {
    if (!trace) return null;
    return (
        <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-[#0f1115] border-l border-white/10 shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-300">
            <div className="p-6 border-b border-white/5 flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        Trace Details
                        <span className="text-xs font-mono text-gray-500 font-normal">#{trace.traceId.substring(0, 8)}...</span>
                    </h2>
                    <p className="text-sm text-gray-400">{new Date(trace.timestamp).toLocaleString()}</p>
                </div>
                <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-lg text-gray-400">
                    <ChevronRight className="w-6 h-6" />
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/5 p-3 rounded-lg">
                        <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Model</p>
                        <p className="text-sm font-medium text-white">{trace.model}</p>
                    </div>
                    <div className="bg-white/5 p-3 rounded-lg">
                        <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Latency</p>
                        <p className="text-sm font-medium text-white">{trace.latencyMs}ms</p>
                    </div>
                    <div className="bg-white/5 p-3 rounded-lg">
                        <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">Tokens/Cost</p>
                        <p className="text-sm font-medium text-white">${trace.costUsd?.toFixed(4)}</p>
                    </div>
                </div>
                <div className="space-y-6">
                    <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <Terminal className="w-3 h-3" /> Input Prompt
                        </h4>
                        <div className="bg-[#1a1b1e] border border-white/5 p-4 rounded-xl font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
                            {trace.prompt}
                        </div>
                    </div>
                    <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <Activity className="w-3 h-3" /> Response
                        </h4>
                        <div className="bg-[#1a1b1e] border border-blue-500/10 p-4 rounded-xl font-mono text-sm text-blue-50/90 whitespace-pre-wrap leading-relaxed">
                            {trace.completion || (trace.error_message && <span className="text-red-400">{trace.error_message}</span>)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
