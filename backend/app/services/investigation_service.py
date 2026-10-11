import math
from datetime import timedelta

from backend.app.services.database import db


TRAFFIC_COLLECTION = db["traffic_anomalies"]
URL_COLLECTION = db["url_access_anomalies"]


def get_top_traffic_anomaly_ips(range_hours: int, limit: int, page: int = 1):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    if page <= 0:
        page = 1

    # Find the latest timestamp available in the dataset.
    latest_record = TRAFFIC_COLLECTION.find_one(
        {},
        {
            "_id": 0,
            "window_start": 1
        },
        sort=[("window_start", -1)]
    )

    if not latest_record:
        return {
            "data_source": "historical_dataset",
            "range": {
                "start_time": None,
                "end_time": None
            },
            "page": page,
            "limit": limit,
            "total_items": 0,
            "total_pages": 1,
            "total_anomaly_windows": 0,
            "data": []
        }

    end_time = latest_record["window_start"]
    start_time = end_time - timedelta(hours=range_hours)

    pipeline = [
        {
            "$match": {
                "window_start": {
                    "$gte": start_time,
                    "$lte": end_time
                },
                "is_anomaly": True
            }
        },
        {
            "$group": {
                "_id": "$ip",
                "anomaly_count": {
                    "$sum": 1
                },
                "total_requests": {
                    "$sum": "$request_count"
                },
                "max_request_count": {
                    "$max": "$request_count"
                },
                "max_robust_z_score": {
                    "$max": "$robust_z_score"
                },
                "first_anomaly": {
                    "$min": "$window_start"
                },
                "last_anomaly": {
                    "$max": "$window_start"
                }
            }
        },
        {
            "$sort": {
                "anomaly_count": -1,
                "max_robust_z_score": -1
            }
        },
        {
            "$facet": {
                "metadata": [{"$count": "total"}],
                "data": [
                    {"$skip": (page - 1) * limit},
                    {"$limit": limit}
                ]
            }
        }
    ]

    results = list(TRAFFIC_COLLECTION.aggregate(pipeline))
    facet_res = results[0] if results else {"metadata": [], "data": []}
    total_items = facet_res["metadata"][0]["total"] if facet_res.get("metadata") else 0
    raw_data = facet_res.get("data", [])

    data = []
    for result in raw_data:
        data.append({
            "ip": result["_id"],
            "anomaly_count": result["anomaly_count"],
            "total_requests": result["total_requests"],
            "max_request_count": result["max_request_count"],
            "max_robust_z_score": result["max_robust_z_score"],
            "first_anomaly": result["first_anomaly"].isoformat() if result.get("first_anomaly") else None,
            "last_anomaly": result["last_anomaly"].isoformat() if result.get("last_anomaly") else None
        })

    # Count all anomaly windows in the selected period.
    total_anomaly_windows = TRAFFIC_COLLECTION.count_documents({
        "window_start": {
            "$gte": start_time,
            "$lte": end_time
        },
        "is_anomaly": True
    })

    return {
        "data_source": "historical_dataset",
        "range": {
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None
        },
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / limit) if total_items > 0 else 1,
        "total_anomaly_windows": total_anomaly_windows,
        "data": data
    }


def get_top_url_anomaly_ips(range_hours: int, limit: int, page: int = 1):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    if page <= 0:
        page = 1

    # Find the latest timestamp available in the dataset.
    latest_record = URL_COLLECTION.find_one(
        {},
        {
            "_id": 0,
            "window_start": 1
        },
        sort=[("window_start", -1)]
    )

    if not latest_record:
        return {
            "data_source": "historical_dataset",
            "range": {
                "start_time": None,
                "end_time": None
            },
            "page": page,
            "limit": limit,
            "total_items": 0,
            "total_pages": 1,
            "total_anomaly_windows": 0,
            "data": []
        }

    end_time = latest_record["window_start"]
    start_time = end_time - timedelta(hours=range_hours)

    pipeline = [
        {
            "$match": {
                "window_start": {
                    "$gte": start_time,
                    "$lte": end_time
                },
                "is_anomaly": True
            }
        },
        {
            "$group": {
                "_id": "$ip",
                "anomaly_count": {
                    "$sum": 1
                },
                "total_unique_url_count": {
                    "$sum": "$unique_url_count"
                },
                "max_unique_url_count": {
                    "$max": "$unique_url_count"
                },
                "max_robust_z_score": {
                    "$max": "$robust_z_score"
                },
                "first_anomaly": {
                    "$min": "$window_start"
                },
                "last_anomaly": {
                    "$max": "$window_start"
                }
            }
        },
        {
            "$sort": {
                "anomaly_count": -1,
                "max_robust_z_score": -1
            }
        },
        {
            "$facet": {
                "metadata": [{"$count": "total"}],
                "data": [
                    {"$skip": (page - 1) * limit},
                    {"$limit": limit}
                ]
            }
        }
    ]

    results = list(URL_COLLECTION.aggregate(pipeline))
    facet_res = results[0] if results else {"metadata": [], "data": []}
    total_items = facet_res["metadata"][0]["total"] if facet_res.get("metadata") else 0
    raw_data = facet_res.get("data", [])

    data = []
    for result in raw_data:
        data.append({
            "ip": result["_id"],
            "anomaly_count": result["anomaly_count"],
            "total_unique_url_count": result["total_unique_url_count"],
            "max_unique_url_count": result["max_unique_url_count"],
            "max_robust_z_score": result["max_robust_z_score"],
            "first_anomaly": result["first_anomaly"].isoformat() if result.get("first_anomaly") else None,
            "last_anomaly": result["last_anomaly"].isoformat() if result.get("last_anomaly") else None
        })

    # Count all URL anomaly windows in the selected period.
    total_anomaly_windows = URL_COLLECTION.count_documents({
        "window_start": {
            "$gte": start_time,
            "$lte": end_time
        },
        "is_anomaly": True
    })

    return {
        "data_source": "historical_dataset",
        "range": {
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None
        },
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / limit) if total_items > 0 else 1,
        "total_anomaly_windows": total_anomaly_windows,
        "data": data
    }