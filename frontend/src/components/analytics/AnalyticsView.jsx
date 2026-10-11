import React, { useState } from 'react';
import { Activity, AlertTriangle, Link2, ShieldAlert } from 'lucide-react';
import TrendDetailView from './TrendDetailView';
import ThreatIpDetailView from '../dashboard/ThreatIpDetailView';

export default function AnalyticsView() {
  const [activeSubTab, setActiveSubTab] = useState('traffic'); // 'traffic' | 'error' | 'url' | 'threats'
  const [threatType, setThreatType] = useState('traffic');

  const tabs = [
    { id: 'traffic', label: 'Traffic Spike Trend', icon: Activity },
    { id: 'error', label: 'Error Rate Trend', icon: AlertTriangle },
    { id: 'url', label: 'URL Access Trend', icon: Link2 },
    { id: 'threats', label: 'Threat IP Explorer', icon: ShieldAlert },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Analytics Sub-navigation Pills */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-100 rounded-2xl w-fit border border-slate-200/60">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-white text-blue-700 shadow-sm border border-slate-200/50'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/40'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Tab Content */}
      {activeSubTab === 'traffic' && <TrendDetailView type="traffic" />}
      {activeSubTab === 'error' && <TrendDetailView type="error" />}
      {activeSubTab === 'url' && <TrendDetailView type="url" />}

      {activeSubTab === 'threats' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setThreatType('traffic')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                threatType === 'traffic'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              Traffic Threat IPs
            </button>
            <button
              onClick={() => setThreatType('url')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                threatType === 'url'
                  ? 'bg-amber-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              URL Scraping Threat IPs
            </button>
          </div>
          <ThreatIpDetailView type={threatType} />
        </div>
      )}
    </div>
  );
}
