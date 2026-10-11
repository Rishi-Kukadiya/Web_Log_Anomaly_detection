import React, { useEffect, useState } from 'react';
import { BarChart2, Link2, ArrowLeft } from 'lucide-react';
import { api, MOCK_TOP_TRAFFIC_IPS, MOCK_TOP_URL_IPS } from '../../services/api';
import { useDashboard } from '../../context/DashboardContext';

export default function ThreatIpDetailView({ type, onBack }) {
  const { timeRange, setTimeRange, rangeHours } = useDashboard();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const isTraffic = type === 'traffic';

  const timePills = [
    { label: '1H', value: '1h' },
    { label: '6H', value: '6h' },
    { label: '24H', value: '24h' },
    { label: '72H', value: '72h' },
    { label: '7D', value: '7d' },
  ];

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const fetcher = isTraffic ? api.getTopTrafficIps : api.getTopUrlIps;
        const res = await fetcher(rangeHours, 10);
        if (isMounted) {
          if (res && res.data && res.data.length > 0) {
            // Find max count for severity calculation
            const maxAnomalies = Math.max(...res.data.map(d => d.anomaly_count || 1), 1);
            const formatted = res.data.map((item, index) => {
              const count = item.anomaly_count || 0;
              const severityPct = Math.min(Math.round((count / maxAnomalies) * 100), 100);
              return {
                rank: index + 1,
                ip: item.ip,
                anomaly_count: count,
                metric_total: isTraffic 
                  ? (item.total_requests || item.max_request_count * 3 || 0)
                  : (item.total_unique_url_count || item.max_unique_url_count * 2 || 0),
                metric_peak: isTraffic 
                  ? (item.max_request_count || 0)
                  : (item.max_unique_url_count || 0),
                max_robust_z_score: item.max_robust_z_score ? Number(item.max_robust_z_score).toFixed(2) : "0.00",
                severity: severityPct
              };
            });
            setData(formatted);
          } else {
            setData(isTraffic ? MOCK_TOP_TRAFFIC_IPS : MOCK_TOP_URL_IPS);
          }
        }
      } catch (err) {
        if (isMounted) setData(isTraffic ? MOCK_TOP_TRAFFIC_IPS : MOCK_TOP_URL_IPS);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => { isMounted = false; };
  }, [type, rangeHours, isTraffic]);

  const title = isTraffic ? 'Top Traffic-Anomaly IPs' : 'Top URL-Anomaly IPs';
  const subtitle = isTraffic
    ? 'IP addresses with the most traffic spike anomalies'
    : 'IP addresses with the most unusual URL access activity';
  const Icon = isTraffic ? BarChart2 : Link2;
  const iconBg = isTraffic ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-500';

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 md:p-8 shadow-sm">
      {/* Top Controls: Back button & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-100">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 flex items-center justify-center text-slate-600 transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0 shadow-sm`}>
            <Icon className="w-6 h-6" />
          </div>

          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              {title}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {subtitle}
            </p>
          </div>
        </div>

        {/* Time Filter Pill Buttons */}
        <div className="flex items-center bg-slate-100/80 p-1 rounded-xl border border-slate-200/60 self-start md:self-auto">
          {timePills.map((pill) => {
            const isActive = timeRange === pill.value;
            return (
              <button
                key={pill.value}
                onClick={() => setTimeRange(pill.value)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                }`}
              >
                {pill.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Data Table */}
      <div className="overflow-x-auto mt-6">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500">
              <th className="py-3.5 pr-4 font-semibold text-slate-400 w-10">#</th>
              <th className="py-3.5 px-4 font-semibold text-slate-700">IP Address</th>
              
              {/* Highlighted active sort column */}
              <th className="py-3.5 px-4 font-bold text-blue-700 bg-blue-50/70 rounded-t-lg">
                <span className="flex items-center gap-1">
                  Anomaly Count
                  <span className="text-blue-600">↓</span>
                </span>
              </th>

              <th className="py-3.5 px-4 text-right font-semibold text-slate-700">
                {isTraffic ? 'Total Requests' : 'Total Unique URLs'}
              </th>
              <th className="py-3.5 px-4 text-right font-semibold text-slate-700">
                {isTraffic ? 'Peak Requests' : 'Max Unique URLs'}
              </th>
              <th className="py-3.5 px-4 text-right font-semibold text-slate-700">Max Z-Score</th>
              <th className="py-3.5 px-4 text-right font-semibold text-slate-700">Severity</th>
              <th className="py-3.5 pl-4 font-semibold text-slate-700 w-52">Activity Bar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((row) => (
              <tr key={row.ip} className="hover:bg-slate-50/80 transition-colors">
                <td className="py-4 pr-4 text-slate-400 font-medium">{row.rank}</td>
                <td className="py-4 px-4 font-mono font-medium text-slate-900">{row.ip}</td>
                
                {/* Active Anomaly Count Column */}
                <td className="py-4 px-4 font-bold text-rose-600 font-mono bg-blue-50/30">
                  {row.anomaly_count}
                </td>

                <td className="py-4 px-4 text-right text-slate-700 font-mono">
                  {row.metric_total?.toLocaleString()}
                </td>
                <td className="py-4 px-4 text-right text-slate-700 font-mono">
                  {row.metric_peak?.toLocaleString()}
                </td>
                <td className="py-4 px-4 text-right font-semibold text-rose-600 font-mono">
                  {row.max_robust_z_score}
                </td>
                <td className="py-4 px-4 text-right font-medium text-slate-700 font-mono">
                  {row.severity}%
                </td>
                
                {/* Visual Severity / Activity Progress Bar */}
                <td className="py-4 pl-4">
                  <div className="w-44 bg-slate-100 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-rose-400 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(row.severity, 6)}%` }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
