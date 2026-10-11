import React, { useEffect, useState } from 'react';
import { api, MOCK_TOP_TRAFFIC_IPS } from '../../services/api';
import { useDashboard } from '../../context/DashboardContext';

export default function TopTrafficTable({ onViewAll }) {
  const { rangeHours } = useDashboard();
  const [ips, setIps] = useState(MOCK_TOP_TRAFFIC_IPS.slice(0, 5));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const res = await api.getTopTrafficIps(rangeHours, 5);
        if (isMounted) {
          if (res && res.data && res.data.length > 0) {
            const formatted = res.data.map((item, index) => ({
              rank: index + 1,
              ip: item.ip,
              anomaly_count: item.anomaly_count,
              total_requests: item.total_requests || 0,
              peak_requests: item.max_request_count || 0,
              max_robust_z_score: item.max_robust_z_score ? Number(item.max_robust_z_score).toFixed(2) : "0.00",
            }));
            setIps(formatted);
          } else {
            setIps([]);
          }
        }
      } catch (err) {
        if (isMounted) setIps(MOCK_TOP_TRAFFIC_IPS.slice(0, 5));
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => { isMounted = false; };
  }, [rangeHours]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Top Traffic-Anomaly IPs
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            IP addresses with the most traffic spike anomalies
          </p>
        </div>

        <button
          onClick={onViewAll}
          className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline transition-colors focus:outline-none"
        >
          View All
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500 font-medium">
              <th className="pb-3 pr-3 font-semibold text-slate-400">#</th>
              <th className="pb-3 pr-4 font-semibold text-slate-600">IP Address</th>
              <th className="pb-3 px-3 text-center font-semibold text-slate-600">Anomaly Count</th>
              <th className="pb-3 px-3 text-right font-semibold text-slate-600">Total Requests</th>
              <th className="pb-3 px-3 text-right font-semibold text-slate-600">Peak Requests</th>
              <th className="pb-3 pl-3 text-right font-semibold text-slate-600">Max Z-Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {ips.map((row) => (
              <tr key={row.ip} className="hover:bg-slate-50/70 transition-colors">
                <td className="py-3 pr-3 text-slate-400 font-medium">{row.rank}</td>
                <td className="py-3 pr-4 font-mono font-medium text-slate-800">{row.ip}</td>
                <td className="py-3 px-3 text-center font-semibold text-rose-600 font-mono">
                  {row.anomaly_count}
                </td>
                <td className="py-3 px-3 text-right text-slate-700 font-mono">
                  {row.total_requests?.toLocaleString()}
                </td>
                <td className="py-3 px-3 text-right text-slate-700 font-mono">
                  {row.peak_requests?.toLocaleString()}
                </td>
                <td className="py-3 pl-3 text-right font-semibold text-rose-600 font-mono">
                  {row.max_robust_z_score}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
