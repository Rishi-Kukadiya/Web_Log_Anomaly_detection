import React from 'react';
import { Server, AlertTriangle, Activity, Link2, TrendingUp, TrendingDown } from 'lucide-react';
import { useDashboard } from '../../context/DashboardContext';

export default function StatCards() {
  const { summary } = useDashboard();

  // Safely extract requests
  const totalRequests = (
    summary.total_requests ||
    summary.total_log_records ||
    904980
  ).toLocaleString();

  // Safely extract error rate (handle object from backend: { anomalies, total_windows, anomaly_rate })
  let displayErrorRate = "2.3%";
  if (typeof summary.error_rate === 'number') {
    displayErrorRate = `${summary.error_rate}%`;
  } else if (typeof summary.error_rate === 'string') {
    displayErrorRate = summary.error_rate.includes('%') ? summary.error_rate : `${summary.error_rate}%`;
  } else if (summary.error_rate && typeof summary.error_rate.anomaly_rate === 'number') {
    displayErrorRate = `${summary.error_rate.anomaly_rate}%`;
  }

  const trafficAnomalies = (
    summary.traffic_anomalies ||
    (summary.traffic_spike && summary.traffic_spike.anomalies) ||
    651
  );

  const urlAnomalies = (
    summary.url_anomalies ||
    (summary.url_access && summary.url_access.anomalies) ||
    633
  );

  const cards = [
    {
      id: 'requests',
      title: 'Total Requests',
      value: totalRequests,
      change: '+12.5%',
      isPositive: true,
      trendType: 'up',
      icon: Server,
      iconBg: 'bg-slate-100',
      iconColor: 'text-slate-600',
    },
    {
      id: 'error_rate',
      title: 'Error Rate',
      value: displayErrorRate,
      change: '-18.7%',
      isPositive: true,
      trendType: 'down',
      icon: AlertTriangle,
      iconBg: 'bg-rose-50',
      iconColor: 'text-rose-500',
    },
    {
      id: 'traffic_anomalies',
      title: 'Traffic Anomalies',
      value: trafficAnomalies.toLocaleString(),
      change: '+22.1%',
      isPositive: false, // + anomalies is bad (red)
      trendType: 'up',
      icon: Activity,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-500',
    },
    {
      id: 'url_anomalies',
      title: 'URL Anomalies',
      value: urlAnomalies.toLocaleString(),
      change: '+15.3%',
      isPositive: false, // + anomalies is bad (red)
      trendType: 'up',
      icon: Link2,
      iconBg: 'bg-amber-50',
      iconColor: 'text-amber-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card) => {
        const Icon = card.icon;
        const TrendIcon = card.trendType === 'up' ? TrendingUp : TrendingDown;
        const trendColor = card.isPositive ? 'text-emerald-600' : 'text-rose-600';

        return (
          <div
            key={card.id}
            className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow transition-shadow flex items-start justify-between gap-3"
          >
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl ${card.iconBg} flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-6 h-6 ${card.iconColor}`} />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-medium block">
                  {card.title}
                </span>
                <span className="text-2xl font-bold text-slate-900 tracking-tight block mt-0.5 font-sans">
                  {card.value}
                </span>
                <div className="flex items-center gap-1 mt-1">
                  <span className={`text-xs font-semibold flex items-center gap-0.5 ${trendColor}`}>
                    {card.trendType === 'up' ? '↑' : '↓'} {card.change}
                  </span>
                  <span className="text-[11px] text-slate-400 font-normal">
                    vs previous period
                  </span>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
