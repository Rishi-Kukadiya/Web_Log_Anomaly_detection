import React, { useState } from 'react';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import AppLayout from './components/layout/AppLayout';
import StatCards from './components/dashboard/StatCards';
import TrafficTrendChart from './components/dashboard/TrafficTrendChart';
import ErrorRateTrendChart from './components/dashboard/ErrorRateTrendChart';
import UrlAccessTrendChart from './components/dashboard/UrlAccessTrendChart';
import TopTrafficTable from './components/dashboard/TopTrafficTable';
import TopUrlTable from './components/dashboard/TopUrlTable';
import ThreatIpDetailView from './components/dashboard/ThreatIpDetailView';
import TrendDetailView from './components/analytics/TrendDetailView';
import AnalyticsView from './components/analytics/AnalyticsView';
import SettingsView from './components/settings/SettingsView';

function MainRouter() {
  const { activeTab } = useDashboard();
  const [threatDetail, setThreatDetail] = useState(null); // 'traffic' | 'url' | null
  const [trendDetail, setTrendDetail] = useState(null);   // 'traffic' | 'error' | 'url' | null

  // Route 1: Analytics Screen (from Sidebar)
  if (activeTab === 'analytics') {
    return <AnalyticsView />;
  }

  // Route 2: Settings Screen (from Sidebar)
  if (activeTab === 'settings') {
    return <SettingsView />;
  }

  // Route 3: Deep Threat IP Drilldown (Screenshots 2 & 5)
  if (threatDetail) {
    return (
      <div className="pb-12">
        <ThreatIpDetailView
          type={threatDetail}
          onBack={() => setThreatDetail(null)}
        />
      </div>
    );
  }

  // Route 4: Deep Trend Drilldown with 4-Metric Telemetry (Screenshots 3, 4, 6)
  if (trendDetail) {
    return (
      <div className="pb-12">
        <TrendDetailView
          type={trendDetail}
          onBack={() => setTrendDetail(null)}
        />
      </div>
    );
  }

  // Route 5: Main Dashboard Overview (Screenshot 1)
  return (
    <div className="space-y-6 pb-12">
      {/* 4 KPI / Metric Cards */}
      <StatCards />

      {/* Row 1: Traffic Trend & Error Rate Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrafficTrendChart onExpand={() => setTrendDetail('traffic')} />
        <ErrorRateTrendChart onExpand={() => setTrendDetail('error')} />
      </div>

      {/* Row 2: URL Access Trend (Full Width) */}
      <div className="w-full">
        <UrlAccessTrendChart onExpand={() => setTrendDetail('url')} />
      </div>

      {/* Row 3: Threat Investigation Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopTrafficTable onViewAll={() => setThreatDetail('traffic')} />
        <TopUrlTable onViewAll={() => setThreatDetail('url')} />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <DashboardProvider>
      <AppLayout>
        <MainRouter />
      </AppLayout>
    </DashboardProvider>
  );
}
