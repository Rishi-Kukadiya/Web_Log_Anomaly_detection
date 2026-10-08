from datetime import timedelta

from backend.app.services.database import db


TRAFFIC_COLLECTION = db["traffic_anomalies"]
URL_COLLECTION = db["url_access_anomalies"]


def get_top_traffic_anomaly_ips(range_hours: int, limit: int):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

    if limit <= 0:
        raise ValueError("limit must be greater than 0")

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
            "limit": limit,
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
            "$limit": limit
        }
    ]

    results = TRAFFIC_COLLECTION.aggregate(pipeline)

    data = []

    for result in results:
        data.append({
            "ip": result["_id"],
            "anomaly_count": result["anomaly_count"],
            "total_requests": result["total_requests"],
            "max_request_count": result["max_request_count"],
            "max_robust_z_score": result["max_robust_z_score"],
            "first_anomaly": result["first_anomaly"],
            "last_anomaly": result["last_anomaly"]
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
            "start_time": start_time,
            "end_time": end_time
        },
        "limit": limit,
        "total_anomaly_windows": total_anomaly_windows,
        "data": data
    }
    
    
def get_top_url_anomaly_ips(range_hours: int, limit: int):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

    if limit <= 0:
        raise ValueError("limit must be greater than 0")

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
            "limit": limit,
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
            "$limit": limit
        }
    ]

    results = URL_COLLECTION.aggregate(pipeline)

    data = []

    for result in results:
        data.append({
            "ip": result["_id"],
            "anomaly_count": result["anomaly_count"],
            "total_unique_url_count": result["total_unique_url_count"],
            "max_unique_url_count": result["max_unique_url_count"],
            "max_robust_z_score": result["max_robust_z_score"],
            "first_anomaly": result["first_anomaly"],
            "last_anomaly": result["last_anomaly"]
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
            "start_time": start_time,
            "end_time": end_time
        },
        "limit": limit,
        "total_anomaly_windows": total_anomaly_windows,
        "data": data
    }