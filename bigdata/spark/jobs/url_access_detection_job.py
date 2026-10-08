from pyspark.sql import SparkSession

from anomaly_detection.url_access.url_access_detector import (
    detect_url_access_anomalies
)


spark = (
    SparkSession.builder
    .appName("URLAccessAnomalyDetection")
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/url_access_aggregation/"
    "url_access_5min.parquet"
)

OUTPUT_PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "url_access"
)

print("\n=== READING INPUT ===")
print(INPUT_PATH)

df = spark.read.parquet(INPUT_PATH)

print("\n=== INPUT RECORD COUNT ===")
print(df.count())

print("\n=== RUNNING URL ACCESS ANOMALY DETECTION ===")

result = detect_url_access_anomalies(df)

print("\n=== WRITING OUTPUT ===")

(
    result
    .write
    .mode("overwrite")
    .parquet(OUTPUT_PATH)
)

print("\n=== OUTPUT WRITTEN ===")
print(OUTPUT_PATH)

spark.stop()
