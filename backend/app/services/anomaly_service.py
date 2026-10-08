from backend.app.services.database import db
from datetime import timedelta


TRAFFIC_COLLECTION = db["traffic_anomalies"]
ERROR_COLLECTION = db["error_rate_anomalies"]
URL_COLLECTION = db["url_access_anomalies"]


def get_dashboard_summary():
    total_log_records = 10_365_075

    traffic_records = TRAFFIC_COLLECTION.count_documents({})
    error_records = ERROR_COLLECTION.count_documents({})
    url_records = URL_COLLECTION.count_documents({})

    traffic_anomalies = TRAFFIC_COLLECTION.count_documents({
        "is_anomaly": True
    })

    error_anomalies = ERROR_COLLECTION.count_documents({
        "is_anomaly": True
    })

    url_anomalies = URL_COLLECTION.count_documents({
        "is_anomaly": True
    })

    total_anomaly_events = (
        traffic_anomalies
        + error_anomalies
        + url_anomalies
    )

    traffic_anomaly_rate = (
        traffic_anomalies / traffic_records * 100
        if traffic_records else 0
    )

    error_anomaly_rate = (
        error_anomalies / error_records * 100
        if error_records else 0
    )

    url_anomaly_rate = (
        url_anomalies / url_records * 100
        if url_records else 0
    )

    total_detector_windows = (
        traffic_records
        + error_records
        + url_records
    )

    overall_anomaly_rate = (
        total_anomaly_events / total_detector_windows * 100
        if total_detector_windows else 0
    )

    return {
        "total_log_records": total_log_records,
        "total_anomaly_events": total_anomaly_events,

        "traffic_spike": {
            "anomalies": traffic_anomalies,
            "total_windows": traffic_records,
            "anomaly_rate": round(traffic_anomaly_rate, 2)
        },

        "error_rate": {
            "anomalies": error_anomalies,
            "total_windows": error_records,
            "anomaly_rate": round(error_anomaly_rate, 2)
        },

        "url_access": {
            "anomalies": url_anomalies,
            "total_windows": url_records,
            "anomaly_rate": round(url_anomaly_rate, 2)
        },

        "overall_anomaly_rate": round(overall_anomaly_rate, 2)
    }


def get_traffic_trend(range_hours: int):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

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
            "interval_minutes": None,
            "total_requests": 0,
            "anomaly_windows": 0,
            "data": []
        }

    end_time = latest_record["window_start"]
    start_time = end_time - timedelta(hours=range_hours)

    # Select graph resolution automatically.
    if range_hours <= 1:
        interval_minutes = 5
    elif range_hours <= 6:
        interval_minutes = 15
    elif range_hours <= 24:
        interval_minutes = 60
    elif range_hours <= 72:
        interval_minutes = 180
    else:
        interval_minutes = 360

    pipeline = [
        {
            "$match": {
                "window_start": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateTrunc": {
                        "date": "$window_start",
                        "unit": "minute",
                        "binSize": interval_minutes
                    }
                },
                "request_count": {
                    "$sum": "$request_count"
                },
                "anomaly_windows": {
                    "$sum": {
                        "$cond": [
                            "$is_anomaly",
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    results = TRAFFIC_COLLECTION.aggregate(pipeline)

    data = []
    total_requests = 0
    total_anomaly_windows = 0

    for result in results:
        request_count = result["request_count"]
        anomaly_windows = result["anomaly_windows"]

        total_requests += request_count
        total_anomaly_windows += anomaly_windows

        bucket_time = result["_id"]
        bucket_end = bucket_time + timedelta(minutes=interval_minutes)

        data.append({
            "time": bucket_time,
            "bucket_end": bucket_end,
            "request_count": request_count,
            "anomaly_windows": anomaly_windows
        })

    return {
        "data_source": "historical_dataset",
        "range": {
            "start_time": start_time,
            "end_time": end_time
        },
        "interval_minutes": interval_minutes,
        "total_requests": total_requests,
        "anomaly_windows": total_anomaly_windows,
        "data": data
    }
    
    
def get_error_rate_trend(range_hours: int):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

    # Find the latest timestamp available in the dataset.
    latest_record = ERROR_COLLECTION.find_one(
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
            "interval_minutes": None,
            "total_requests": 0,
            "total_errors": 0,
            "overall_error_rate": 0,
            "anomaly_windows": 0,
            "data": []
        }

    end_time = latest_record["window_start"]
    start_time = end_time - timedelta(hours=range_hours)

    # Automatically select graph resolution.
    if range_hours <= 1:
        interval_minutes = 5
    elif range_hours <= 6:
        interval_minutes = 15
    elif range_hours <= 24:
        interval_minutes = 60
    elif range_hours <= 72:
        interval_minutes = 180
    else:
        interval_minutes = 360

    pipeline = [
        {
            "$match": {
                "window_start": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateTrunc": {
                        "date": "$window_start",
                        "unit": "minute",
                        "binSize": interval_minutes
                    }
                },
                "total_requests": {
                    "$sum": "$total_requests"
                },
                "error_requests": {
                    "$sum": "$error_requests"
                },
                "anomaly_windows": {
                    "$sum": {
                        "$cond": [
                            "$is_anomaly",
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    results = ERROR_COLLECTION.aggregate(pipeline)

    data = []
    total_requests = 0
    total_errors = 0
    total_anomaly_windows = 0

    for result in results:
        bucket_total_requests = result["total_requests"]
        bucket_error_requests = result["error_requests"]
        bucket_anomaly_windows = result["anomaly_windows"]

        bucket_error_rate = (
            bucket_error_requests / bucket_total_requests
            if bucket_total_requests > 0
            else 0
        )

        total_requests += bucket_total_requests
        total_errors += bucket_error_requests
        total_anomaly_windows += bucket_anomaly_windows

        bucket_time = result["_id"]
        bucket_end = bucket_time + timedelta(minutes=interval_minutes)

        data.append({
            "time": bucket_time,
            "bucket_end": bucket_end,
            "total_requests": bucket_total_requests,
            "error_requests": bucket_error_requests,
            "error_rate": round(bucket_error_rate, 4),
            "anomaly_windows": bucket_anomaly_windows
        })

    overall_error_rate = (
        total_errors / total_requests
        if total_requests > 0
        else 0
    )

    return {
        "data_source": "historical_dataset",
        "range": {
            "start_time": start_time,
            "end_time": end_time
        },
        "interval_minutes": interval_minutes,
        "total_requests": total_requests,
        "total_errors": total_errors,
        "overall_error_rate": round(overall_error_rate, 4),
        "anomaly_windows": total_anomaly_windows,
        "data": data
    }
    
    
    
def get_url_access_trend(range_hours: int):
    if range_hours <= 0:
        raise ValueError("range_hours must be greater than 0")

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
            "interval_minutes": None,
            "total_unique_url_accesses": 0,
            "anomaly_windows": 0,
            "data": []
        }

    end_time = latest_record["window_start"]
    start_time = end_time - timedelta(hours=range_hours)

    # Automatically select graph resolution.
    if range_hours <= 1:
        interval_minutes = 5
    elif range_hours <= 6:
        interval_minutes = 15
    elif range_hours <= 24:
        interval_minutes = 60
    elif range_hours <= 72:
        interval_minutes = 180
    else:
        interval_minutes = 360

    pipeline = [
        {
            "$match": {
                "window_start": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateTrunc": {
                        "date": "$window_start",
                        "unit": "minute",
                        "binSize": interval_minutes
                    }
                },
                "unique_url_accesses": {
                    "$sum": "$unique_url_count"
                },
                "anomaly_windows": {
                    "$sum": {
                        "$cond": [
                            "$is_anomaly",
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    results = URL_COLLECTION.aggregate(pipeline)

    data = []
    total_unique_url_accesses = 0
    total_anomaly_windows = 0

    for result in results:
        unique_url_accesses = result["unique_url_accesses"]
        anomaly_windows = result["anomaly_windows"]

        total_unique_url_accesses += unique_url_accesses
        total_anomaly_windows += anomaly_windows

        bucket_time = result["_id"]
        bucket_end = bucket_time + timedelta(minutes=interval_minutes)

        data.append({
            "time": bucket_time,
            "bucket_end": bucket_end,
            "unique_url_accesses": unique_url_accesses,
            "anomaly_windows": anomaly_windows
        })

    return {
        "data_source": "historical_dataset",
        "range": {
            "start_time": start_time,
            "end_time": end_time
        },
        "interval_minutes": interval_minutes,
        "total_unique_url_accesses": total_unique_url_accesses,
        "anomaly_windows": total_anomaly_windows,
        "data": data
    }