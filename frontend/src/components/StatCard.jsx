import React from 'react';

export default function StatCard({ title, value, unit, icon: Icon, colorClass }) {
    return (
        <div className="bg-[#1a1b1e] border border-white/5 p-5 rounded-xl shadow-sm hover:border-white/10 transition-colors">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2 rounded-lg ${colorClass} bg-opacity-10`}>
                    <Icon className={`w-5 h-5 ${colorClass.replace('bg-', 'text-')}`} />
                </div>
            </div>
            <div>
                <p className="text-gray-400 text-sm font-medium">{title}</p>
                <div className="flex items-baseline gap-1 mt-1">
                    <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
                    {unit && <span className="text-gray-500 text-sm">{unit}</span>}
                </div>
            </div>
        </div>
    );
}
