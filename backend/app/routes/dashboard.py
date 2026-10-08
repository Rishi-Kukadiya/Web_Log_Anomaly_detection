from fastapi import APIRouter
from datetime import datetime
from backend.app.services.anomaly_service import (
    get_dashboard_summary,
    get_traffic_trend,
    get_error_rate_trend,
    get_url_access_trend
)


from backend.app.services.investigation_service import (
    get_top_traffic_anomaly_ips,
    get_top_url_anomaly_ips
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary():
    return get_dashboard_summary()

@router.get("/traffic-trend")
def traffic_trend(range_hours: int = 24):
    if range_hours not in [1, 6, 24, 72, 168]:
        return {
            "error": "range_hours must be one of: 1, 6, 24, 72, 168"
        }

    return get_traffic_trend(range_hours)


@router.get("/error-rate-trend")
def error_rate_trend(range_hours: int = 24):
    if range_hours not in [1, 6, 24, 72, 168]:
        return {
            "error": "range_hours must be one of: 1, 6, 24, 72, 168"
        }

    return get_error_rate_trend(range_hours)


@router.get("/url-access-trend")
def url_access_trend(range_hours: int = 24):
    if range_hours not in [1, 6, 24, 72, 168]:
        return {
            "error": "range_hours must be one of: 1, 6, 24, 72, 168"
        }

    return get_url_access_trend(range_hours)



@router.get("/top-traffic-anomaly-ips")
def top_traffic_anomaly_ips(
    range_hours: int = 24,
    limit: int = 10
):
    if range_hours not in [1, 6, 24, 72, 168]:
        return {
            "error": "range_hours must be one of: 1, 6, 24, 72, 168"
        }

    if limit not in [5, 10, 20, 50]:
        return {
            "error": "limit must be one of: 5, 10, 20, 50"
        }

    return get_top_traffic_anomaly_ips(
        range_hours,
        limit
    )
    
    
@router.get("/top-url-anomaly-ips")
def top_url_anomaly_ips(
    range_hours: int = 24,
    limit: int = 10
):
    if range_hours not in [1, 6, 24, 72, 168]:
        return {
            "error": "range_hours must be one of: 1, 6, 24, 72, 168"
        }

    if limit not in [5, 10, 20, 50]:
        return {
            "error": "limit must be one of: 5, 10, 20, 50"
        }

    return get_top_url_anomaly_ips(
        range_hours,
        limit
    )