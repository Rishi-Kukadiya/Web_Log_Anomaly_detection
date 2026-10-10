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
    try {
      const data = await api.getSummary();
      if (data && !data.error) {
        setSummary((prev) => ({ ...prev, ...data }));
      }
    } catch (err) {
      console.error("Failed to refresh summary:", err);
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
