import React, { useState } from 'react';
import { Database, Sliders, ShieldCheck, HardDrive, RefreshCw } from 'lucide-react';
import { useDashboard } from '../../context/DashboardContext';

export default function SettingsView() {
  const { summary, refreshSummary, loading } = useDashboard();
  const [minHistory, setMinHistory] = useState(5);
  const [zScoreThreshold, setZScoreThreshold] = useState(3.5);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="max-w-4xl space-y-6 pb-12">
      {/* Cluster & Analytical Store Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 md:p-8 shadow-sm space-y-5">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">Database & Analytical Store</h2>
              <p className="text-xs text-slate-500">Active storage and HDFS replication configuration</p>
            </div>
          </div>
          <button
            onClick={refreshSummary}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Sync Telemetry
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1">
            <span className="text-slate-400 font-medium">Database Name</span>
            <span className="font-mono font-bold text-slate-800 text-sm">log_analytics</span>
            <span className="text-emerald-600 font-semibold flex items-center gap-1 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Connected & Indexed
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1">
            <span className="text-slate-400 font-medium">HDFS Cluster</span>
            <span className="font-mono font-bold text-slate-800 text-sm">hdfs://node1:9000/</span>
            <span className="text-slate-500 mt-1">3 Hadoop Nodes Active (Replication factor: 2)</span>
          </div>
        </div>
      </div>

      {/* Anomaly Detection Statistical Engine Settings */}
      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200/80 p-6 md:p-8 shadow-sm space-y-6">
        <div className="flex items-center gap-3.5 pb-4 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">Statistical Thresholds (MAD & Z-Score)</h2>
            <p className="text-xs text-slate-500">Explainable unsupervised anomaly detection parameters</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1.5">
              Robust Z-Score Threshold (Standard: 3.5)
            </label>
            <input
              type="number"
              step="0.1"
              value={zScoreThreshold}
              onChange={(e) => setZScoreThreshold(parseFloat(e.target.value))}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[11px] text-slate-400 mt-1.5">
              Windows with Modified Z-Score ≥ {zScoreThreshold} are flagged as anomalous.
            </p>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1.5">
              Minimum History Window Count (Standard: 5)
            </label>
            <input
              type="number"
              value={minHistory}
              onChange={(e) => setMinHistory(parseInt(e.target.value))}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[11px] text-slate-400 mt-1.5">
              Number of preceding 5-min windows required to calculate rolling IP baseline.
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {saved ? (
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> Parameters saved successfully!
            </span>
          ) : <span></span>}

          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-colors shadow-sm"
          >
            Save Parameters
          </button>
        </div>
      </form>
    </div>
  );
}
