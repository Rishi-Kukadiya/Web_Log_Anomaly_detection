import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useDashboard } from '../../context/DashboardContext';
import { Copy, Check, Radio } from 'lucide-react';

export default function TopTrafficTable({ onViewAll }) {
  const { rangeHours } = useDashboard();
  const [ips, setIps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiedIp, setCopiedIp] = useState(null);
  const [totalAnomalies, setTotalAnomalies] = useState(0);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const res = await api.getTopTrafficIps(rangeHours, 5);
        console.log(res)
        if (isMounted) {
          if (res && res.data && Array.isArray(res.data)) {
            const formatted = res.data.map((item, index) => ({
              rank: index + 1,
              ip: item.ip,
              anomaly_count: item.anomaly_count || 0,
              total_requests: item.total_requests || 0,
              peak_requests: item.max_request_count || 0,
              max_robust_z_score: item.max_robust_z_score != null ? Number(item.max_robust_z_score).toFixed(2) : "0.00",
            }));
            setIps(formatted);
            setTotalAnomalies(res.total_anomaly_windows || 0);
          } else {
            setIps([]);
            setTotalAnomalies(0);
          }
        }
      } catch (err) {
        console.error("Failed to fetch top traffic anomaly IPs:", err);
        if (isMounted) {
          setIps([]);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => { isMounted = false; };
  }, [rangeHours]);

  const handleCopy = (ip) => {
    navigator.clipboard?.writeText(ip);
    setCopiedIp(ip);
    setTimeout(() => setCopiedIp(null), 1500);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              Top Traffic-Anomaly IPs
            </h2>
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Live DB
            </span>
          </div>
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
      <div className="overflow-x-auto min-h-[220px]">
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
            {loading ? (
              // Loading Skeleton
              Array.from({ length: 5 }).map((_, idx) => (
                <tr key={`skeleton-${idx}`} className="animate-pulse">
                  <td className="py-3.5 pr-3"><div className="h-3.5 w-3 bg-slate-100 rounded"></div></td>
                  <td className="py-3.5 pr-4"><div className="h-3.5 w-28 bg-slate-100 rounded"></div></td>
                  <td className="py-3.5 px-3"><div className="h-3.5 w-8 bg-slate-100 rounded mx-auto"></div></td>
                  <td className="py-3.5 px-3"><div className="h-3.5 w-12 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-3.5 px-3"><div className="h-3.5 w-10 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-3.5 pl-3"><div className="h-3.5 w-12 bg-slate-100 rounded ml-auto"></div></td>
                </tr>
              ))
            ) : ips.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-400">
                  No traffic anomalies detected in this time range.
                </td>
              </tr>
            ) : (
              ips.map((row) => (
                <tr key={row.ip} className="hover:bg-slate-50/70 transition-colors group">
                  <td className="py-3 pr-3 text-slate-400 font-medium">{row.rank}</td>
                  <td className="py-3 pr-4 font-mono font-medium text-slate-800">
                    <button
                      onClick={() => handleCopy(row.ip)}
                      title="Click to copy IP"
                      className="inline-flex items-center gap-1.5 hover:text-blue-600 transition-colors text-left"
                    >
                      <span>{row.ip}</span>
                      {copiedIp === row.ip ? (
                        <Check className="w-3 h-3 text-emerald-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </button>
                  </td>
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
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
