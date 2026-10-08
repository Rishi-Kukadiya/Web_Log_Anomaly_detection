from pyspark.sql import SparkSession

from anomaly_detection.error_rate.error_rate_detector import (
    detect_error_rate_anomalies
)


spark = (
    SparkSession.builder
    .appName("TestErrorRateDetector")
    .config(
        "spark.hadoop.fs.defaultFS",
        "hdfs://node1:9000"
    )
    .getOrCreate()
)

INPUT_PATH = (
    "hdfs://node1:9000/data/error_rate_aggregation/"
    "error_rate_5min.parquet"
)


# ---------------------------------------------------------
# Read input
# ---------------------------------------------------------

df = spark.read.parquet(INPUT_PATH)


# ---------------------------------------------------------
# Run anomaly detector
# ---------------------------------------------------------

result = detect_error_rate_anomalies(df)


# ---------------------------------------------------------
# Schema
# ---------------------------------------------------------

print("\n=== RESULT SCHEMA ===")
result.printSchema()


# ---------------------------------------------------------
# Total records
# ---------------------------------------------------------

print("\n=== TOTAL RECORDS ===")
print(result.count())


# ---------------------------------------------------------
# Anomaly summary
# ---------------------------------------------------------

print("\n=== ANOMALY SUMMARY ===")
(
    result
    .groupBy("is_error_rate_anomaly")
    .count()
    .show()
)


# ---------------------------------------------------------
# Top anomalies
# ---------------------------------------------------------

print("\n=== TOP ERROR RATE ANOMALIES ===")

(
    result
    .filter("is_error_rate_anomaly = true")
    .orderBy("error_rate", ascending=False)
    .select(
        "ip",
        "window_start",
        "window_end",
        "total_requests",
        "error_requests",
        "error_rate",
        "history_count",
        "baseline_median",
        "mad",
        "history_age_hours",
        "robust_z_score"
    )
    .show(20, truncate=False)
)


spark.stop()