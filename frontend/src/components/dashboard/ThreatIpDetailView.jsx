import React, { useEffect, useState } from 'react';
import { BarChart2, Link2, ArrowLeft, Copy, Check, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { api } from '../../services/api';
import { useDashboard } from '../../context/DashboardContext';

export default function ThreatIpDetailView({ type, onBack }) {
  const { timeRange, setTimeRange, rangeHours } = useDashboard();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiedIp, setCopiedIp] = useState(null);

  // Pagination states
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const isTraffic = type === 'traffic';

  const timePills = [
    { label: '1H', value: '1h' },
    { label: '6H', value: '6h' },
    { label: '24H', value: '24h' },
    { label: '72H', value: '72h' },
    { label: '7D', value: '7d' },
  ];

  const pageSizeOptions = [10, 20, 50];

  // Reset to page 1 whenever time range or page size changes
  useEffect(() => {
    setPage(1);
  }, [rangeHours, pageSize]);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const fetcher = isTraffic ? api.getTopTrafficIps : api.getTopUrlIps;
        const res = await fetcher(rangeHours, pageSize, page);
        if (isMounted) {
          if (res && res.data && Array.isArray(res.data) && res.data.length > 0) {
            const returnedTotal = res.total_items ?? res.data.length;
            const calcTotalPages = res.total_pages ?? Math.max(Math.ceil(returnedTotal / pageSize), 1);
            setTotalItems(returnedTotal);
            setTotalPages(calcTotalPages);

            // Find peak anomaly count across this page for relative activity bar
            const maxAnomalies = Math.max(...res.data.map(d => d.anomaly_count || 1), 1);
            const rankOffset = (page - 1) * pageSize;

            const formatted = res.data.map((item, index) => {
              const count = item.anomaly_count || 0;
              const severityPct = Math.min(Math.round((count / maxAnomalies) * 100), 100);
              return {
                rank: rankOffset + index + 1,
                ip: item.ip,
                anomaly_count: count,
                metric_total: isTraffic 
                  ? (item.total_requests || 0)
                  : (item.total_unique_url_count || 0),
                metric_peak: isTraffic 
                  ? (item.max_request_count || 0)
                  : (item.max_unique_url_count || 0),
                max_robust_z_score: item.max_robust_z_score != null ? Number(item.max_robust_z_score).toFixed(2) : "0.00",
                severity: severityPct
              };
            });
            setData(formatted);
          } else {
            setData([]);
            setTotalItems(0);
            setTotalPages(1);
          }
        }
      } catch (err) {
        console.error("Failed to fetch threat IP details:", err);
        if (isMounted) {
          setData([]);
          setTotalItems(0);
          setTotalPages(1);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => { isMounted = false; };
  }, [type, rangeHours, isTraffic, page, pageSize]);

  const handleCopy = (ip) => {
    navigator.clipboard?.writeText(ip);
    setCopiedIp(ip);
    setTimeout(() => setCopiedIp(null), 1500);
  };

  const title = isTraffic ? 'Top Traffic-Anomaly IPs' : 'Top URL-Anomaly IPs';
  const subtitle = isTraffic
    ? 'IP addresses with the most traffic spike anomalies detected from server logs'
    : 'IP addresses with the most unusual URL access activity detected from server logs';
  const Icon = isTraffic ? BarChart2 : Link2;
  const iconBg = isTraffic ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-500';

  // Calculate visible page buttons (window of 5 pages around current page)
  const getVisiblePages = () => {
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  const startRecord = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const endRecord = Math.min(page * pageSize, totalItems);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 md:p-8 shadow-sm">
      {/* Top Controls: Back button, Title & Time Range Filter */}
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
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                {title}
              </h1>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Live DB
              </span>
            </div>
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
      <div className="overflow-x-auto mt-6 min-h-[360px]">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-500">
              <th className="py-3.5 pr-4 font-semibold text-slate-400 w-12">#</th>
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
            {loading ? (
              Array.from({ length: pageSize }).map((_, idx) => (
                <tr key={`skel-${idx}`} className="animate-pulse">
                  <td className="py-4 pr-4"><div className="h-4 w-5 bg-slate-100 rounded"></div></td>
                  <td className="py-4 px-4"><div className="h-4 w-32 bg-slate-100 rounded"></div></td>
                  <td className="py-4 px-4 bg-blue-50/20"><div className="h-4 w-10 bg-slate-100 rounded"></div></td>
                  <td className="py-4 px-4"><div className="h-4 w-16 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-4 px-4"><div className="h-4 w-12 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-4 px-4"><div className="h-4 w-14 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-4 px-4"><div className="h-4 w-10 bg-slate-100 rounded ml-auto"></div></td>
                  <td className="py-4 pl-4"><div className="h-3 w-40 bg-slate-100 rounded-full"></div></td>
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-16 text-center text-slate-400">
                  No anomaly records detected in this time range.
                </td>
              </tr>
            ) : (
              data.map((row) => (
                <tr key={row.ip} className="hover:bg-slate-50/80 transition-colors group">
                  <td className="py-4 pr-4 text-slate-400 font-medium">{row.rank}</td>
                  <td className="py-4 px-4 font-mono font-medium text-slate-900">
                    <button
                      onClick={() => handleCopy(row.ip)}
                      title="Click to copy IP"
                      className="inline-flex items-center gap-1.5 hover:text-blue-600 transition-colors text-left"
                    >
                      <span>{row.ip}</span>
                      {copiedIp === row.ip ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="w-3.5 h-3.5 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </button>
                  </td>
                  
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
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 mt-4 border-t border-slate-100 text-xs">
        {/* Left: Range and total information */}
        <div className="flex items-center gap-3 text-slate-500">
          <span>
            Showing <span className="font-semibold text-slate-800">{startRecord}</span> to{' '}
            <span className="font-semibold text-slate-800">{endRecord}</span> of{' '}
            <span className="font-semibold text-slate-800">{totalItems.toLocaleString()}</span> anomalous IPs
          </span>

          <span className="text-slate-300">|</span>

          {/* Rows per page selector */}
          <div className="flex items-center gap-1.5">
            <span>Rows:</span>
            <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200">
              {pageSizeOptions.map((opt) => (
                <button
                  key={opt}
                  onClick={() => setPageSize(opt)}
                  className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                    pageSize === opt
                      ? 'bg-white text-blue-700 shadow-sm'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Page navigation controls */}
        <div className="flex items-center gap-1">
          {/* First page */}
          <button
            onClick={() => setPage(1)}
            disabled={page === 1 || loading}
            className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="First Page"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>

          {/* Previous page */}
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {/* Page numbers */}
          {getVisiblePages().map((pNum) => (
            <button
              key={pNum}
              onClick={() => setPage(pNum)}
              disabled={loading}
              className={`w-8 h-8 rounded-lg font-semibold transition-all ${
                page === pNum
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              {pNum}
            </button>
          ))}

          {/* Next page */}
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || loading}
            className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          {/* Last page */}
          <button
            onClick={() => setPage(totalPages)}
            disabled={page === totalPages || loading}
            className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Last Page"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
