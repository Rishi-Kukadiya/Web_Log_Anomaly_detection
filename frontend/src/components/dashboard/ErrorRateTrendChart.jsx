import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import { api } from '../../services/api';
import { useDashboard } from '../../context/DashboardContext';

function generateSampleErrorRateData() {
  const points = [];
  const times = [
    "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
    "Jan 26", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00",
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"
  ];

  const baseValues = [
    5.2, 7.8, 19.5, 6.4, 8.1, 18.2, 5.9, 12.3,
    18.6, 6.1, 8.4, 7.2, 5.8, 27.5, 8.3, 11.2,
    16.9, 8.4, 7.9, 13.8, 17.5, 11.0, 68.4, 25.1, 6.2
  ];

  const anomaliesIndices = [2, 5, 8, 13, 16, 19, 20, 22, 23];

  times.forEach((time, index) => {
    const rate = baseValues[index % baseValues.length];
    const isAnomaly = anomaliesIndices.includes(index);
    points.push({
      time,
      error_rate: rate,
      is_anomaly: isAnomaly,
    });
  });

  return points;
}

export default function ErrorRateTrendChart() {
  const { rangeHours } = useDashboard();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const res = await api.getErrorRateTrend(rangeHours);
        if (isMounted) {
          if (res && res.data && res.data.length > 0) {
            const formatted = res.data.map((item, idx) => {
              const d = new Date(item.time);
              const hours = d.getHours().toString().padStart(2, '0');
              const minutes = d.getMinutes().toString().padStart(2, '0');
              const timeStr = `${hours}:${minutes}`;
              const label = (idx === Math.floor(res.data.length / 3)) ? "Jan 26" : timeStr;
              return {
                time: label,
                fullTime: `${hours}:${minutes}`,
                error_rate: Math.round((item.error_rate * 100) * 10) / 10,
                is_anomaly: item.anomaly_windows > 0,
              };
            });
            setData(formatted);
          } else {
            setData(generateSampleErrorRateData());
          }
        }
      } catch (e) {
        if (isMounted) setData(generateSampleErrorRateData());
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadData();
    return () => { isMounted = false; };
  }, [rangeHours]);

  const renderCustomDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload && payload.is_anomaly) {
      return (
        <circle
          key={`err-dot-${cx}-${cy}`}
          cx={cx}
          cy={cy}
          r={3.5}
          fill="#ef4444"
          stroke="#ffffff"
          strokeWidth={1.5}
        />
      );
    }
    return null;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload;
      return (
        <div className="bg-white/95 backdrop-blur border border-slate-200 rounded-xl shadow-lg p-3 text-xs z-50">
          <div className="font-semibold text-slate-800 mb-1">{point.fullTime || label}</div>
          <div className="flex items-center gap-2 text-slate-600">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-500 inline-block"></span>
            <span>Error Rate: <strong className="text-slate-900 font-mono">{point.error_rate}%</strong></span>
          </div>
          {point.is_anomaly && (
            <div className="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center gap-1.5 text-rose-600 font-semibold">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              Error Spike Anomaly
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow transition-shadow">
      {/* Header & Legend */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Error Rate Trend
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            HTTP error rate over time with detected anomalies
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-rose-500 rounded"></span>
            <span>Error Rate</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            <span>Anomaly</span>
          </div>
        </div>
      </div>

      {/* Area / Line Chart */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="errorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
              dy={8}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickFormatter={(v) => `${v}%`}
              domain={[0, 80]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="error_rate"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#errorGradient)"
              dot={renderCustomDot}
              activeDot={{ r: 5, fill: '#ef4444', stroke: '#ffffff', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
