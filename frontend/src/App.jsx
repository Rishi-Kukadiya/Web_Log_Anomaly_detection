import React from 'react';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import AppLayout from './components/layout/AppLayout';
import { ShieldCheck, Activity, Server, AlertTriangle } from 'lucide-react';

function DashboardContent() {
  const { summary, loading } = useDashboard();

  return (
    <div className="space-y-6">
      {/* Foundation Status Banner for Commit 1 */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-6 shadow-md border border-blue-800/40 relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-semibold mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Frontend Foundation Initialized (Commit 1/5)
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white">
              Log Anomaly Detection Engine
            </h2>
            <p className="text-blue-200 text-xs mt-1 max-w-2xl">
              Nginx Access Log Preprocessor • 3-Node HDFS Cluster • Spark Window Aggregation • Robust MAD Baseline • FastAPI Backend
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl px-4 py-2.5 text-center">
              <span className="text-[10px] text-blue-200 font-medium block uppercase tracking-wider">Total Records</span>
              <span className="text-base font-bold text-white font-mono">10,365,075</span>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl px-4 py-2.5 text-center">
              <span className="text-[10px] text-blue-200 font-medium block uppercase tracking-wider">Detection Windows</span>
              <span className="text-base font-bold text-white font-mono">5-Min Rolling</span>
            </div>
          </div>
        </div>

        {/* Ambient background glow */}
        <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      </div>

      {/* Initial Grid Architecture Preview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
            <Server className="w-6 h-6 text-slate-600" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium">Total Requests</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5 font-mono">904,980</div>
            <span className="text-emerald-600 text-xs font-semibold">↑ +12.5% vs prev</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-6 h-6 text-rose-600" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium">Error Rate</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5 font-mono">2.3%</div>
            <span className="text-emerald-600 text-xs font-semibold">↓ -18.7% vs prev</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
            <Activity className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium">Traffic Anomalies</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5 font-mono">651</div>
            <span className="text-rose-600 text-xs font-semibold">↑ +22.1% vs prev</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium">URL Anomalies</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5 font-mono">633</div>
            <span className="text-rose-600 text-xs font-semibold">↑ +15.3% vs prev</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <DashboardProvider>
      <AppLayout>
        <DashboardContent />
      </AppLayout>
    </DashboardProvider>
  );
}
