import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, MOCK_SUMMARY } from '../services/api';

const DashboardContext = createContext();

export function DashboardProvider({ children }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [timeRange, setTimeRange] = useState('24h'); // '1h', '6h', '24h', '72h', '7d'
  const [summary, setSummary] = useState(MOCK_SUMMARY);
  const [loading, setLoading] = useState(false);

  // Map timeRange string to numeric hours for backend queries
  const getRangeHours = () => {
    switch (timeRange) {
      case '1h': return 1;
      case '6h': return 6;
      case '24h': return 24;
      case '72h': return 72;
      case '7d': return 168;
      default: return 24;
    }
  };

  const refreshSummary = async () => {
    setLoading(true);
    const hours = getRangeHours();
    try {
      // Parallel fetch from real backend database
      const [sumRes, trafficRes, errorRes, urlRes] = await Promise.allSettled([
        api.getSummary(),
        api.getTrafficTrend(hours),
        api.getErrorRateTrend(hours),
        api.getUrlAccessTrend(hours),
      ]);

      const updated = { ...MOCK_SUMMARY };

      if (sumRes.status === 'fulfilled' && sumRes.value && !sumRes.value.error) {
        Object.assign(updated, sumRes.value);
      }

      // 1. Process Traffic Trend & Compute Dynamic Period-over-Period Changes
      if (trafficRes.status === 'fulfilled' && trafficRes.value && !trafficRes.value.error) {
        if (trafficRes.value.total_requests !== undefined) {
          updated.total_requests = trafficRes.value.total_requests;
        }
        if (trafficRes.value.anomaly_windows !== undefined) {
          updated.traffic_anomalies = trafficRes.value.anomaly_windows;
        }

        const tData = trafficRes.value.data || [];
        const mid = Math.floor(tData.length / 2);
        if (mid > 0) {
          const prevReq = tData.slice(0, mid).reduce((acc, curr) => acc + (curr.request_count || 0), 0);
          const currReq = tData.slice(mid).reduce((acc, curr) => acc + (curr.request_count || 0), 0);
          const reqDiff = prevReq ? ((currReq - prevReq) / prevReq) * 100 : 0;
          updated.requests_change = `${reqDiff >= 0 ? '+' : ''}${reqDiff.toFixed(1)}%`;
          updated.requests_is_up = reqDiff >= 0;

          const prevAnom = tData.slice(0, mid).reduce((acc, curr) => acc + (curr.anomaly_windows || 0), 0);
          const currAnom = tData.slice(mid).reduce((acc, curr) => acc + (curr.anomaly_windows || 0), 0);
          const anomDiff = prevAnom ? ((currAnom - prevAnom) / prevAnom) * 100 : 0;
          updated.traffic_anomalies_change = `${anomDiff >= 0 ? '+' : ''}${anomDiff.toFixed(1)}%`;
          updated.traffic_anomalies_is_up = anomDiff >= 0;
        }
      }

      // 2. Process Error Rate Trend & Compute Dynamic Period-over-Period Changes
      if (errorRes.status === 'fulfilled' && errorRes.value && !errorRes.value.error) {
        if (errorRes.value.overall_error_rate !== undefined) {
          updated.error_rate = `${(errorRes.value.overall_error_rate * 100).toFixed(1)}%`;
        }

        const eData = errorRes.value.data || [];
        const midE = Math.floor(eData.length / 2);
        if (midE > 0) {
          const prevTot = eData.slice(0, midE).reduce((acc, curr) => acc + (curr.total_requests || 0), 0);
          const prevErr = eData.slice(0, midE).reduce((acc, curr) => acc + (curr.error_requests || 0), 0);
          const currTot = eData.slice(midE).reduce((acc, curr) => acc + (curr.total_requests || 0), 0);
          const currErr = eData.slice(midE).reduce((acc, curr) => acc + (curr.error_requests || 0), 0);

          const prevRate = prevTot ? prevErr / prevTot : 0;
          const currRate = currTot ? currErr / currTot : 0;
          const errDiff = prevRate ? ((currRate - prevRate) / prevRate) * 100 : 0;

          updated.error_rate_change = `${errDiff >= 0 ? '+' : ''}${errDiff.toFixed(1)}%`;
          updated.error_rate_is_up = errDiff >= 0;
        }
      }

      // 3. Process URL Access Trend & Compute Dynamic Period-over-Period Changes
      if (urlRes.status === 'fulfilled' && urlRes.value && !urlRes.value.error) {
        if (urlRes.value.anomaly_windows !== undefined) {
          updated.url_anomalies = urlRes.value.anomaly_windows;
        }

        const uData = urlRes.value.data || [];
        const midU = Math.floor(uData.length / 2);
        if (midU > 0) {
          const prevUAnom = uData.slice(0, midU).reduce((acc, curr) => acc + (curr.anomaly_windows || 0), 0);
          const currUAnom = uData.slice(midU).reduce((acc, curr) => acc + (curr.anomaly_windows || 0), 0);
          const uDiff = prevUAnom ? ((currUAnom - prevUAnom) / prevUAnom) * 100 : 0;

          updated.url_anomalies_change = `${uDiff >= 0 ? '+' : ''}${uDiff.toFixed(1)}%`;
          updated.url_anomalies_is_up = uDiff >= 0;
        }
      }

      setSummary(updated);
    } catch (err) {
      console.warn("Failed to refresh live summary from backend:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSummary();
  }, [timeRange]);

  return (
    <DashboardContext.Provider value={{
      activeTab,
      setActiveTab,
      timeRange,
      setTimeRange,
      rangeHours: getRangeHours(),
      summary,
      loading,
      refreshSummary
    }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
}
