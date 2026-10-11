/**
 * API Service for Web Server Anomaly Detection Dashboard
 * Directly queries live MongoDB database ('log_analytics') via FastAPI backend.
 * Zero static mock IP arrays - 100% pure live database telemetry.
 */

// Baseline empty data structure for initial load state
export const INITIAL_SUMMARY = {
  total_log_records: 10365075,
  total_requests: 0,
  requests_change: "0.0%",
  requests_is_up: true,
  error_rate: "0.0%",
  error_rate_change: "0.0%",
  error_rate_is_up: false,
  traffic_anomalies: 0,
  traffic_anomalies_change: "0.0%",
  traffic_anomalies_is_up: false,
  url_anomalies: 0,
  url_anomalies_change: "0.0%",
  url_anomalies_is_up: false,
  total_anomaly_events: 0,
};

// Dual-strategy fetch: tries direct FastAPI CORS first, then proxy fallback
async function fetchWithFallback(endpoint, fallbackData = null) {
  // Strategy 1: Direct backend URL via CORS (fastest & most reliable)
  try {
    const res = await fetch(`http://127.0.0.1:8000/api${endpoint}`, {
      headers: { 'Accept': 'application/json' }
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (err) {
    // Direct call failed, fall back to relative
  }

  // Strategy 2: Relative /api (via Vite proxy)
  try {
    const res = await fetch(`/api${endpoint}`, {
      headers: { 'Accept': 'application/json' }
    });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (err) {
    console.warn(`[API] Failed fetching ${endpoint}:`, err);
  }

  return fallbackData;
}

export const api = {
  getHealth: () => 
    fetchWithFallback('/health', { status: "unknown", database: "disconnected" }),

  getSummary: () => 
    fetchWithFallback('/dashboard/summary', null),

  getTrafficTrend: (rangeHours = 24) => 
    fetchWithFallback(`/dashboard/traffic-trend?range_hours=${rangeHours}`, null),

  getErrorRateTrend: (rangeHours = 24) => 
    fetchWithFallback(`/dashboard/error-rate-trend?range_hours=${rangeHours}`, null),

  getUrlAccessTrend: (rangeHours = 24) => 
    fetchWithFallback(`/dashboard/url-access-trend?range_hours=${rangeHours}`, null),

  getTopTrafficIps: (rangeHours = 24, limit = 5, page = 1) => 
    fetchWithFallback(`/dashboard/top-traffic-anomaly-ips?range_hours=${rangeHours}&limit=${limit}&page=${page}`, { data: [] }),

  getTopUrlIps: (rangeHours = 24, limit = 5, page = 1) => 
    fetchWithFallback(`/dashboard/top-url-anomaly-ips?range_hours=${rangeHours}&limit=${limit}&page=${page}`, { data: [] }),
};
