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

      if (trafficRes.status === 'fulfilled' && trafficRes.value) {
        if (trafficRes.value.total_requests) {
          updated.total_requests = trafficRes.value.total_requests;
        }
        if (trafficRes.value.anomaly_windows !== undefined) {
          updated.traffic_anomalies = trafficRes.value.anomaly_windows;
        }
      }

      if (errorRes.status === 'fulfilled' && errorRes.value) {
        if (errorRes.value.overall_error_rate !== undefined) {
          updated.error_rate = `${(errorRes.value.overall_error_rate * 100).toFixed(1)}%`;
        }
      }

      if (urlRes.status === 'fulfilled' && urlRes.value) {
        if (urlRes.value.anomaly_windows !== undefined) {
          updated.url_anomalies = urlRes.value.anomaly_windows;
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
