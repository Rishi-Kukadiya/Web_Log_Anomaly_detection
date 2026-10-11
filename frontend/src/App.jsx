import React, { useState } from 'react';
import { DashboardProvider } from './context/DashboardContext';
import AppLayout from './components/layout/AppLayout';
import StatCards from './components/dashboard/StatCards';
import TrafficTrendChart from './components/dashboard/TrafficTrendChart';
import ErrorRateTrendChart from './components/dashboard/ErrorRateTrendChart';
import UrlAccessTrendChart from './components/dashboard/UrlAccessTrendChart';
import TopTrafficTable from './components/dashboard/TopTrafficTable';
import TopUrlTable from './components/dashboard/TopUrlTable';
import ThreatIpDetailView from './components/dashboard/ThreatIpDetailView';

function DashboardView() {
  const [detailView, setDetailView] = useState(null); // null | 'traffic' | 'url'

  if (detailView) {
    return (
      <div className="pb-12">
        <ThreatIpDetailView
          type={detailView}
          onBack={() => setDetailView(null)}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* 4 KPI / Metric Cards */}
      <StatCards />

      {/* Row 1: Traffic Trend & Error Rate Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrafficTrendChart />
        <ErrorRateTrendChart />
      </div>

      {/* Row 2: URL Access Trend (Full Width) */}
      <div className="w-full">
        <UrlAccessTrendChart />
      </div>

      {/* Row 3: Threat Investigation Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopTrafficTable onViewAll={() => setDetailView('traffic')} />
        <TopUrlTable onViewAll={() => setDetailView('url')} />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <DashboardProvider>
      <AppLayout>
        <DashboardView />
      </AppLayout>
    </DashboardProvider>
  );
}
