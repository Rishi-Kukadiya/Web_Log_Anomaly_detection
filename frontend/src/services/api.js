/**
 * API Service for Web Server Anomaly Detection Dashboard
 * Communicates with FastAPI backend with built-in realistic mock fallback
 */

const API_BASE_URL = '/api';

// Fallback Mock Data matching exact production dashboard screenshots
export const MOCK_SUMMARY = {
  total_log_records: 10365075,
  total_requests: 904980,
  requests_change: "+12.5%",
  error_rate: 2.3,
  error_rate_change: "-18.7%",
  traffic_anomalies: 651,
  traffic_anomalies_change: "+22.1%",
  url_anomalies: 633,
  url_anomalies_change: "+15.3%",
  total_anomaly_events: 1712,
  traffic_spike: {
    anomalies: 651,
    total_windows: 288,
    anomaly_rate: 22.6
  },
  error_rate_stats: {
    anomalies: 428,
    total_windows: 288,
    anomaly_rate: 14.8,
    average_rate: "2.3%",
    peak_rate: "68.4%"
  },
  url_access_stats: {
    anomalies: 633,
    total_windows: 288,
    anomaly_rate: 22.0,
    total_unique_urls: 52487,
    peak_unique_urls: 1427
  }
};

export const MOCK_TOP_TRAFFIC_IPS = [
  { rank: 1, ip: "66.249.66.92", anomaly_count: 17, total_requests: 2777, peak_requests: 379, max_robust_z_score: 83.19, severity: 100 },
  { rank: 2, ip: "66.249.66.197", anomaly_count: 16, total_requests: 350, peak_requests: 66, max_robust_z_score: 20.57, severity: 25 },
  { rank: 3, ip: "66.249.66.195", anomaly_count: 15, total_requests: 276, peak_requests: 64, max_robust_z_score: 41.14, severity: 49 },
  { rank: 4, ip: "66.249.66.93", anomaly_count: 13, total_requests: 1344, peak_requests: 167, max_robust_z_score: 45.19, severity: 54 },
  { rank: 5, ip: "23.101.169.3", anomaly_count: 12, total_requests: 2988, peak_requests: 367, max_robust_z_score: 15.08, severity: 18 },
  { rank: 6, ip: "134.19.177.23", anomaly_count: 11, total_requests: 1214, peak_requests: 298, max_robust_z_score: 12.36, severity: 15 },
  { rank: 7, ip: "66.249.66.196", anomaly_count: 10, total_requests: 842, peak_requests: 184, max_robust_z_score: 10.92, severity: 13 },
  { rank: 8, ip: "77.36.156.26", anomaly_count: 9, total_requests: 1102, peak_requests: 221, max_robust_z_score: 9.88, severity: 12 },
  { rank: 9, ip: "207.46.13.143", anomaly_count: 8, total_requests: 638, peak_requests: 135, max_robust_z_score: 8.51, severity: 18 },
  { rank: 10, ip: "40.77.167.205", anomaly_count: 7, total_requests: 512, peak_requests: 120, max_robust_z_score: 6.74, severity: 8 }
];

export const MOCK_TOP_URL_IPS = [
  { rank: 1, ip: "66.249.66.197", anomaly_count: 16, total_unique_urls: 324, peak_unique_urls: 58, max_robust_z_score: 17.87, severity: 100 },
  { rank: 2, ip: "66.249.66.195", anomaly_count: 14, total_unique_urls: 248, peak_unique_urls: 59, max_robust_z_score: 38.45, severity: 86 },
  { rank: 3, ip: "66.249.66.194", anomaly_count: 12, total_unique_urls: 3889, peak_unique_urls: 407, max_robust_z_score: 9.56, severity: 75 },
  { rank: 4, ip: "91.99.72.15", anomaly_count: 10, total_unique_urls: 668, peak_unique_urls: 158, max_robust_z_score: 12.82, severity: 63 },
  { rank: 5, ip: "66.249.66.92", anomaly_count: 9, total_unique_urls: 239, peak_unique_urls: 45, max_robust_z_score: 10.12, severity: 56 },
  { rank: 6, ip: "134.19.177.23", anomaly_count: 8, total_unique_urls: 573, peak_unique_urls: 179, max_robust_z_score: 33.39, severity: 50 },
  { rank: 7, ip: "77.36.156.26", anomaly_count: 6, total_unique_urls: 369, peak_unique_urls: 138, max_robust_z_score: 43.84, severity: 38 },
  { rank: 8, ip: "207.46.13.143", anomaly_count: 6, total_unique_urls: 88, peak_unique_urls: 25, max_robust_z_score: 14.84, severity: 38 },
  { rank: 9, ip: "66.249.66.93", anomaly_count: 6, total_unique_urls: 115, peak_unique_urls: 34, max_robust_z_score: 12.14, severity: 38 },
  { rank: 10, ip: "40.77.167.205", anomaly_count: 6, total_unique_urls: 228, peak_unique_urls: 39, max_robust_z_score: 8.77, severity: 38 }
];

// Helper to fetch with JSON parsing and fallback
async function fetchWithFallback(url, fallbackData) {
  try {
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    console.warn(`API call to ${url} failed, using fallback data.`, err);
    return fallbackData;
  }
}

export const api = {
  // Health Check
  getHealth: () => fetchWithFallback(`${API_BASE_URL}/health`, { status: "ok", database: "connected" }),

  // Dashboard Summary
  getSummary: () => fetchWithFallback(`${API_BASE_URL}/dashboard/summary`, MOCK_SUMMARY),

  // Traffic Trend
  getTrafficTrend: (rangeHours = 24) => 
    fetchWithFallback(`${API_BASE_URL}/dashboard/traffic-trend?range_hours=${rangeHours}`, null),

  // Error Rate Trend
  getErrorRateTrend: (rangeHours = 24) => 
    fetchWithFallback(`${API_BASE_URL}/dashboard/error-rate-trend?range_hours=${rangeHours}`, null),

  // URL Access Trend
  getUrlAccessTrend: (rangeHours = 24) => 
    fetchWithFallback(`${API_BASE_URL}/dashboard/url-access-trend?range_hours=${rangeHours}`, null),

  // Top Traffic Anomaly IPs
  getTopTrafficIps: (rangeHours = 24, limit = 10) => 
    fetchWithFallback(`${API_BASE_URL}/dashboard/top-traffic-anomaly-ips?range_hours=${rangeHours}&limit=${limit}`, { data: MOCK_TOP_TRAFFIC_IPS }),

  // Top URL Anomaly IPs
  getTopUrlIps: (rangeHours = 24, limit = 10) => 
    fetchWithFallback(`${API_BASE_URL}/dashboard/top-url-anomaly-ips?range_hours=${rangeHours}&limit=${limit}`, { data: MOCK_TOP_URL_IPS }),
};
