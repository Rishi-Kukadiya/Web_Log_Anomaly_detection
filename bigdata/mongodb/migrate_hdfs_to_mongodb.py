from pyspark.sql import SparkSession
from pymongo import MongoClient, UpdateOne


# =========================================================
# CONFIGURATION
# =========================================================

MONGO_URI = "mongodb://172.17.176.1:27017/"
DATABASE = "web_server_anomaly_detection"

BATCH_SIZE = 1000


DATASETS = {
    "traffic": {
        "input": "hdfs://node1:9000/data/anomaly_detection/traffic_spike",
        "collection": "traffic_anomalies",
    },
    "error_rate": {
        "input": "hdfs://node1:9000/data/anomaly_detection/error_rate",
        "collection": "error_rate_anomalies",
    },
    "url_access": {
        "input": "hdfs://node1:9000/data/anomaly_detection/url_access",
        "collection": "url_access_anomalies",
    },
}


# =========================================================
# SPARK
# =========================================================

spark = (
    SparkSession.builder
    .appName("HDFS-to-MongoDB-Migration")
    .getOrCreate()
)


# =========================================================
# DOCUMENT TRANSFORMATION
# =========================================================

def create_document(row, dataset_type):

    data = row.asDict()

    document = {
        "ip": data["ip"],
        "window_start": data["window_start"],
        "window_end": data["window_end"],
        "history": {
            "count": data["history_count"],
            "baseline_median": data["baseline_median"],
            "mad": data["mad"],
            "age_hours": data["history_age_hours"],
        },
        "robust_z_score": data["robust_z_score"],
    }

    if dataset_type == "traffic":

        document["request_count"] = data["request_count"]
        document["is_anomaly"] = data["is_traffic_spike"]

    elif dataset_type == "error_rate":

        document["total_requests"] = data["total_requests"]
        document["error_requests"] = data["error_requests"]
        document["error_rate"] = data["error_rate"]
        document["is_anomaly"] = data["is_error_rate_anomaly"]

    elif dataset_type == "url_access":

        document["unique_url_count"] = data["unique_url_count"]
        document["is_anomaly"] = data["is_url_access_anomaly"]

    return document


# =========================================================
# PARTITION MIGRATION
# =========================================================

def migrate_partition(rows, dataset_type, collection_name):

    # Create MongoDB connection INSIDE the Spark worker.
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    collection = client[
        DATABASE
    ][
        collection_name
    ]

    operations = []

    processed = 0

    try:

        for row in rows:

            document = create_document(
                row,
                dataset_type
            )

            operations.append(
                UpdateOne(
                    {
                        "ip": document["ip"],
                        "window_start": document["window_start"],
                    },
                    {
                        "$set": document
                    },
                    upsert=True
                )
            )

            if len(operations) >= BATCH_SIZE:

                collection.bulk_write(
                    operations,
                    ordered=False
                )

                processed += len(operations)

                operations.clear()

        # Write remaining documents.
        if operations:

            collection.bulk_write(
                operations,
                ordered=False
            )

            processed += len(operations)

    finally:

        client.close()

    print(
        f"{dataset_type}: processed {processed} records"
    )


# =========================================================
# DATASET MIGRATION
# =========================================================

def migrate_dataset(dataset_type, config):

    print("\n" + "=" * 60)
    print(f"MIGRATING: {dataset_type}")
    print("=" * 60)

    input_path = config["input"]
    collection_name = config["collection"]

    print(f"Input:      {input_path}")
    print(f"Collection: {collection_name}")

    df = spark.read.parquet(input_path)

    total_records = df.count()

    print(f"Total source records: {total_records}")

    # Create a serializable partition function.
    def process_partition(rows):

        migrate_partition(
            rows,
            dataset_type,
            collection_name
        )

    df.foreachPartition(process_partition)

    print(
        f"{dataset_type}: migration completed."
    )


# =========================================================
# RUN MIGRATIONS
# =========================================================

for dataset_type, config in DATASETS.items():

    migrate_dataset(
        dataset_type,
        config
    )


# =========================================================
# CLEANUP
# =========================================================

spark.stop()

print("\n" + "=" * 60)
print("ALL MIGRATIONS COMPLETED")
print("=" * 60)