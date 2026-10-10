import React from 'react';
import { LayoutGrid, BarChart2, Settings, Shield } from 'lucide-react';
import { useDashboard } from '../../context/DashboardContext';

export default function Sidebar() {
  const { activeTab, setActiveTab } = useDashboard();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0a101f] min-h-screen text-slate-300 flex flex-col flex-shrink-0 select-none border-r border-slate-900/50">
      {/* Brand Header */}
      <div className="p-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/30 flex-shrink-0">
          <Shield className="w-6 h-6 text-white fill-white/20" />
        </div>
        <div className="flex flex-col">
          <span className="text-white font-bold text-lg tracking-wider leading-tight">
            RISHI
          </span>
          <span className="text-slate-400 text-xs font-normal leading-tight mt-0.5">
            Log Anomaly Detection
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-4 py-4 space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-[#1d4ed8] text-white shadow-md shadow-blue-900/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 mx-4 mb-4 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Cluster Connected
        </span>
        <span className="text-slate-500 text-[10px] font-mono">v1.0.0</span>
      </div>
    </aside>
  );
}
