from pyspark.sql import SparkSession

from anomaly_detection.error_rate.error_rate_detector import (
    detect_error_rate_anomalies
)


# ---------------------------------------------------------
# Spark Session
# ---------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("ErrorRateAnomalyDetection")
    .getOrCreate()
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_PATH = (
    "hdfs://node1:9000/data/error_rate_aggregation/"
    "error_rate_5min.parquet"
)

OUTPUT_PATH = (
    "hdfs://node1:9000/data/anomaly_detection/"
    "error_rate"
)


# ---------------------------------------------------------
# Read input from HDFS
# ---------------------------------------------------------

print("\n=== READING INPUT ===")
print(INPUT_PATH)

df = spark.read.parquet(INPUT_PATH)

print("\n=== INPUT RECORD COUNT ===")
print(df.count())


# ---------------------------------------------------------
# Run Error Rate Anomaly Detection
# ---------------------------------------------------------

print("\n=== RUNNING ERROR RATE DETECTION ===")

result = detect_error_rate_anomalies(df)


# ---------------------------------------------------------
# Show schema
# ---------------------------------------------------------

print("\n=== RESULT SCHEMA ===")
result.printSchema()


# ---------------------------------------------------------
# Count results
# ---------------------------------------------------------

print("\n=== TOTAL RECORDS ===")
total_records = result.count()
print(total_records)


print("\n=== ANOMALY SUMMARY ===")

(
    result
    .groupBy("is_error_rate_anomaly")
    .count()
    .orderBy("is_error_rate_anomaly")
    .show()
)


# ---------------------------------------------------------
# Show top anomalies
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


# ---------------------------------------------------------
# Write result to HDFS
# ---------------------------------------------------------

print("\n=== WRITING RESULT TO HDFS ===")
print(OUTPUT_PATH)

(
    result
    .write
    .mode("overwrite")
    .parquet(OUTPUT_PATH)
)


print("\n=== JOB COMPLETED SUCCESSFULLY ===")
print(f"Output: {OUTPUT_PATH}")


spark.stop()
