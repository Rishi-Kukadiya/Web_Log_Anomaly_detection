from pyspark.sql import SparkSession
from pymongo import MongoClient


MONGO_URI = "mongodb://172.17.176.1:27017/"
DATABASE = "web_server_anomaly_detection"
COLLECTION = "traffic_anomalies"

INPUT_PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "traffic_spike"
)


spark = (
    SparkSession.builder
    .appName("MongoDBMigrationTest")
    .getOrCreate()
)


# Read only 10 records
df = (
    spark.read
    .parquet(INPUT_PATH)
    .limit(10)
)


print("\n=== TEST SOURCE RECORDS ===")
print(df.count())


def process_partition(rows):

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    collection = client[
        DATABASE
    ][
        COLLECTION
    ]

    try:

        documents = []

        for row in rows:

            data = row.asDict()

            document = {
                "ip": data["ip"],
                "window_start": data["window_start"],
                "window_end": data["window_end"],
                "request_count": data["request_count"],
                "history": {
                    "count": data["history_count"],
                    "baseline_median": data["baseline_median"],
                    "mad": data["mad"],
                    "age_hours": data["history_age_hours"],
                },
                "robust_z_score": data["robust_z_score"],
                "is_anomaly": data["is_traffic_spike"],
            }

            documents.append(document)

        if documents:

            collection.insert_many(
                documents,
                ordered=False
            )

            print(
                f"Inserted {len(documents)} test documents."
            )

    finally:

        client.close()


df.foreachPartition(process_partition)

spark.stop()

print("\n=== TEST COMPLETED ===")
